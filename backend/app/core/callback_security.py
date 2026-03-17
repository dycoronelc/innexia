"""Validación del token para callbacks desde n8n (header X-Callback-Token)."""
from fastapi import Header, HTTPException, status

from ..config import settings


def validate_callback_token(
    x_callback_token: str | None = Header(default=None, alias="X-Callback-Token"),
) -> None:
    if not settings.CALLBACK_SHARED_TOKEN:
        return
    if not x_callback_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing callback token",
        )
    if x_callback_token != settings.CALLBACK_SHARED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid callback token",
        )
