import asyncio
import random
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException
from openai import OpenAI
from services.llmService import Provider
import json


class NIM(Provider):

    def __init__(self, endpoint: str = "[API_ENDPOINT]", api_key: str = "[ENCRYPTION_KEY]"):
        super().__init__(endpoint=endpoint, api_key=api_key)
        self.aliases = {
            'fast': 'nvidia/nemotron-3.5-lightning-30b-a3b'
        }
        self.provider_name = "NVIDIA"
        self.client = OpenAI(base_url =self.endpoint, api_key = self.api_key)
        # print(self.client.models.list())

    def get_provider_name(self):
        return self.provider_name

    def resolve_alias(self, alias: str) -> str:
        return self.aliases.get(alias, alias)

    def tailor_request(self, model: str, messages: Union[str, List[Any]], **kwargs: Any) -> Any:
        pass

    async def get_response(self, request, model, **kwargs: Any) -> Dict[str, Any]:
        
        response = self.client.chat.completions.create(
            model=model,
            messages=request.messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            stream=request.stream
        )


        if isinstance(response.choices[0].message, str):
            prompt_tokens = len(response.choices[0].message.split())
        elif isinstance(response.choices[0].message, list):
            prompt_tokens = sum(
                len(str(getattr(m, "content", m.get("content", "") if isinstance(m, dict) else m)).split())
                for m in response.choices[0].message
            )
        else:
            prompt_tokens = len(str(response.choices[0].message).split()) if response.choices[0].message else 0

        completion_tokens = len(response.choices[0].message.content.split())

        response.usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }

        return response

    # CamelCase alias
    getResponse = get_response