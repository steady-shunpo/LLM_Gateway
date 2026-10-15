import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from repository.database import save_metric
from repository.providerMetricDTO import ProviderMetricsDTO

logger = logging.getLogger(__name__)


class Provider(ABC):
    """
    Abstract interface for LLM provider services.
    """

    def __init__(self, endpoint: str = "", api_key: str = ""):
        self.endpoint: str = endpoint
        self.api_key: str = api_key
        self.apikey: str = api_key

    @abstractmethod
    def resolve_alias(self, alias: str) -> str:
        """
        Resolve a given model alias to the actual provider model name.
        """
        pass

    @abstractmethod
    def tailor_request(self, request: Any, **kwargs: Any) -> Any:
        """
        Format and prepare the request payload specific to the provider API.
        """
        pass

    @abstractmethod
    async def get_response(self, request: Any, model: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send request to the provider service and return the response.
        """
        pass

    # CamelCase alias
    getResponse = get_response


class LLMService:
    """
    Orchestration service that routes requests across configured providers.
    """

    def __init__(self, provider_list: List[Provider], max_retries: int = 1):
        self.providers: List[Provider] = provider_list
        self.max_retries: int = max_retries
        self.metric_history: List[ProviderMetricsDTO] = []

    async def get_response(self, request: Any, tenant: Optional[str] = None) -> Dict[str, Any]:
        last_exception = None
        runMetrics: List[ProviderMetricsDTO] = []
        actual_tenant = tenant or getattr(request, "tenant", None) or "default"
        for provider in self.providers:
            retries_left = self.max_retries
            while True:
                start_time = time.perf_counter()
                model = getattr(request, "model", None)
                try:
                    model = provider.resolve_alias(request.model)
                    # request.model = model
                    logger.info("Chosen provider: %s for model: %s", provider.__class__.__name__, model)
                    response = await provider.get_response(request, model)

                    # Verify response does not indicate failure
                    if isinstance(response, dict) and response.get("error"):
                        raise RuntimeError(f"Provider returned error: {response['error']}")
                    if hasattr(response, "status_code") and response.status_code >= 400:
                        raise RuntimeError(f"Provider returned status {response.status_code}")

                    latency = time.perf_counter() - start_time
                    logger.info("get_response took %.4f seconds (provider: %s)", latency, provider.__class__.__name__)

                    input_tokens = 0
                    output_tokens = 0
                    usage = getattr(response, "usage", None) if hasattr(response, "usage") else (response.get("usage") if isinstance(response, dict) else None)
                    if usage:
                        if isinstance(usage, dict):
                            input_tokens = usage.get("prompt_tokens", 0)
                            output_tokens = usage.get("completion_tokens", 0)
                        else:
                            input_tokens = getattr(usage, "prompt_tokens", 0)
                            output_tokens = getattr(usage, "completion_tokens", 0)

                    status_code = getattr(response, "status_code", 200) if hasattr(response, "status_code") else (response.get("status_code", 200) if isinstance(response, dict) else 200)

                    metric = ProviderMetricsDTO(
                        tenant=actual_tenant,
                        final_status="success",
                        status_code=status_code,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency=latency,
                        provider_name=getattr(provider, "provider_name", provider.__class__.__name__),
                        model=model,
                    )
                    runMetrics.append(metric)
                    save_metric(metric)

                    return response
                except Exception as e:
                    last_exception = e
                    logger.error("Provider %s threw an exception: %s", provider.__class__.__name__, e, exc_info=True)
                    status_code = getattr(e, "status_code", None)
                    if hasattr(e, "response") and hasattr(e.response, "status_code"):
                        status_code = status_code or e.response.status_code

                    latency = time.perf_counter() - start_time
                    metric = ProviderMetricsDTO(
                        tenant=actual_tenant,
                        final_status="failure",
                        status_code=status_code,
                        input_tokens=0,
                        output_tokens=0,
                        latency=latency,
                        provider_name=getattr(provider, "provider_name", provider.__class__.__name__),
                        model=model,
                    )
                    runMetrics.append(metric)
                    save_metric(metric)

                    # Retry on 429 or 5xx if retries remain
                    if retries_left > 0 and (status_code == 429 or (status_code is not None and status_code >= 500)):
                        retries_left -= 1
                        if status_code == 429:
                            logger.info("Rate limit hit (429) on %s. Retrying after 20s (retries left: %d)...", provider.__class__.__name__, retries_left)
                            await asyncio.sleep(20)
                        else:
                            logger.info("Server error (%s) on %s. Retrying (retries left: %d)...", status_code, provider.__class__.__name__, retries_left)
                        continue

                    # No retries left or non-retryable error: move to next provider
                    break

        if last_exception:
            raise last_exception
        raise RuntimeError("No providers configured in LLMService.")

    # CamelCase alias
    getResponse = get_response
