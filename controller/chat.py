from services.rateLimiter import canAllowRequest
from services import rateLimiter
from services.llmService import LLMService
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from services.fakeProvider1 import Provider1
from services.fakeProvider2 import NIM
from services.authService import get_current_tenant
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(prefix="/v1/chat", tags=["Chat"])
fakeProvider1 = Provider1()
fakeProvider2 = Provider1()
# fakeProvider2 = Provider2()
realProvider1 = NIM(os.environ.get("PROVIDER_ENDPOINT"), os.environ.get("PROVIDER_API_KEY"))


llmService = LLMService([fakeProvider1, fakeProvider2, realProvider1])

class ChatMessage(BaseModel):
    role: str
    content: Union[str, Any]
    name: Optional[str] = None


class CompletionRequest(BaseModel):
    # Standard OpenAI fields
    model: Optional[str] = None
    messages: Optional[Union[List[ChatMessage], List[Dict[str, Any]], str]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    tenant: Optional[str] = None

    # Custom / legacy fields

    class Config:
        extra = "allow"


@router.post("/completions", summary="Create chat completion")
async def completions(
    request: CompletionRequest,
    tenant: str = Depends(get_current_tenant),
):
    if not canAllowRequest(tenant):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in 1 minute."
        )

    model_name = request.model
    if not model_name:
        raise HTTPException(
            status_code=400,
            detail="Missing required field: 'model' or 'alias' must be specified."
        )

    messages = request.messages
    if messages is None:
        raise HTTPException(
            status_code=400,
            detail="Missing required field: 'messages' or 'prompt' must be specified."
        )

    request.tenant = tenant
    response = await llmService.get_response(request, tenant=tenant)
    return response

