import logging
from typing import Optional
from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.keyGenerator import keyGenerator

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def verify_api_key(api_key: str) -> Optional[str]:
    """
    Verifies the raw API key by checking its SHA-256 hash in the database.
    Returns the associated tenant name if valid and active, otherwise None.
    """
    return keyGenerator.verify_key(api_key)


async def get_current_tenant(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    """
    FastAPI dependency for authenticating incoming requests.
    Extracts the API key from:
      1. Authorization header (Bearer token or raw key)
      2. x-api-key header
      3. api-key header
    Validates the key against stored SHA-256 hashes in the database.
    Returns the tenant string on success, or raises 401 Unauthorized.
    """
    api_key: Optional[str] = None

    if credentials and credentials.credentials:
        api_key = credentials.credentials.strip()

    if not api_key:
        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if auth_header:
            if auth_header.lower().startswith("bearer "):
                api_key = auth_header[7:].strip()
            else:
                api_key = auth_header.strip()

    if not api_key:
        api_key = request.headers.get("x-api-key") or request.headers.get("api-key")

    if not api_key:
        logger.warning("Authentication failed: Missing API key in request from %s", request.client.host if request.client else "unknown")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Missing API Key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tenant = verify_api_key(api_key)
    if not tenant:
        logger.warning("Authentication failed: Invalid or revoked API key.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid or revoked API Key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tenant
