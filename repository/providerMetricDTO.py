from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderMetricsDTO:
    """
    DTO capturing execution metrics for a provider attempt.
    """
    tenant: str = "default"
    final_status: str = "failure"  # "success" or "failure"
    status_code: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency: float = 0.0
    provider_name: Optional[str] = None
    model: Optional[str] = None