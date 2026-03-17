from fastapi import Header, HTTPException, status

from app.core.config import settings



def validate_callback_token(x_callback_token: str | None = Header(default=None)) -> None:
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
