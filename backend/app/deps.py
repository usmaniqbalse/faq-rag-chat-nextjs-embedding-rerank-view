from fastapi import Depends, Header, HTTPException, status
from .config import settings

def verify_api_key(x_api_key: str = Header(default=None)):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True
