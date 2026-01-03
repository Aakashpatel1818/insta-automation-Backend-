"""Authentication routes (minimal, error‑free version)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
)

logger = get_logger(__name__)
router = APIRouter(tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    expires_in: int


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest):
    """
    Minimal login stub.

    Currently DOES NOT query DB – you must plug in DB when ready.
    For now it just returns 501 to avoid confusing behavior.
    """

    logger.info(f"Login attempt: {credentials.email}")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login not implemented yet. Add DB lookup in app/api/routes/auth.py",
    )


@router.post("/register", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def register(email: EmailStr, password: str):
    """
    Minimal register stub.

    Same idea: you will implement real DB user creation later.
    """

    logger.info(f"Registration attempt: {email}")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration not implemented yet. Add DB logic in app/api/routes/auth.py",
    )


@router.post("/logout")
async def logout():
    """Simple logout stub – client should just delete tokens locally."""
    logger.info("Logout requested")
    return {"message": "Logged out successfully", "status": "success"}


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Minimal token refresh stub.

    When you add real refresh token verification, replace this stub.
    """
    logger.info("Token refresh requested")

    # For now, just 501 so your API is honest
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token flow not implemented yet. See app/core/security.py.",
    )
