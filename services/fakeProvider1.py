import asyncio
import random
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException
from services.llmService import Provider


class Provider1(Provider):

    def __init__(self, endpoint: str = "[API_ENDPOINT]", api_key: str = "[ENCRYPTION_KEY]"):
        super().__init__(endpoint=endpoint, api_key=api_key)
        self.aliases = {
            'fast': 'gemini-3-flash',
            'smart': 'gemini-3-pro'
        }
        self.provider_name = "FAKE1" 

    def get_provider_name(self):
        return self.provider_name

    def resolve_alias(self, alias: str) -> str:
        return self.aliases.get(alias, alias)

    def tailor_request(self, model: str, messages: Union[str, List[Any]], **kwargs: Any) -> Any:
        pass

    async def get_response(self, request, model, **kwargs: Any) -> Dict[str, Any]:
        outcome = random.choice(["success", "delay", "error_500", "error_429"])

        if outcome == "delay":
            await asyncio.sleep(30)
            content = "Hello this is the delayed response from Provider 1"
        elif outcome == "error_500":
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Provider 1 encountered an unexpected failure."
            )
        elif outcome == "error_429":
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests: Rate limit exceeded for Provider 1."
            )
        else:
            content = "Hello this is the response from Provider 1"

        if isinstance(request.messages, str):
            prompt_tokens = len(request.messages.split())
        elif isinstance(request.messages, list):
            prompt_tokens = sum(
                len(str(getattr(m, "content", m.get("content", "") if isinstance(m, dict) else m)).split())
                for m in request.messages
            )
        else:
            prompt_tokens = len(str(request.messages).split()) if request.messages else 0

        completion_tokens = len(content.split())

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "system_fingerprint": None,
        }

    # CamelCase alias
    getResponse = get_response