"""Security utilities for JWT and password hashing."""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    try:
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}", exc_info=True)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Error verifying password: {e}", exc_info=True)
        return False


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.

    Args:
        data: Token payload (e.g., {"sub": user_id, "email": user_email})
        expires_delta: Custom expiration delta (uses settings.ACCESS_TOKEN_EXPIRE_MINUTES if None)

    Returns:
        JWT access token string
    """
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        logger.debug(f"Access token created for {data.get('sub', 'unknown')}")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating access token: {e}", exc_info=True)
        raise


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token (longer expiration).

    Args:
        data: Token payload (e.g., {"sub": user_id, "email": user_email})
        expires_delta: Custom expiration delta (uses settings.REFRESH_TOKEN_EXPIRE_DAYS if None)

    Returns:
        JWT refresh token string
    """
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        logger.debug(f"Refresh token created for {data.get('sub', 'unknown')}")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating refresh token: {e}", exc_info=True)
        raise


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload dict if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}", exc_info=True)
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Deprecated: Use verify_token() instead.

    Args:
        token: JWT token string

    Returns:
        Token payload dict if valid, None otherwise
    """
    return verify_token(token)