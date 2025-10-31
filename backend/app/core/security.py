from fastapi import Header, HTTPException
from app.core.config import settings

def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-KEY")):
    """
    Simple header guard. Frontend proxy should add the correct X-API-KEY header.
    """
    if not x_api_key or x_api_key != settings.BACKEND_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
