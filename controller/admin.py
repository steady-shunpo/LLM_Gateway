from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from services.keyGenerator import keyGenerator

router = APIRouter(prefix="/v1/admin", tags=["Admin"])


class KeyRequest(BaseModel):
    tenant: Optional[str] = "default"


@router.post("/generate-key", summary="Generate API Key")
async def generate_api_key(request: Optional[KeyRequest] = None, tenant: Optional[str] = None):
    chosen_tenant = (request.tenant if request and request.tenant else None) or tenant or "default"
    api_key = keyGenerator.generate_key(tenant=chosen_tenant)
    return {"api_key": api_key, "tenant": chosen_tenant}