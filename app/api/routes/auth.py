"""Authentication routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from bcrypt import hashpw, checkpw, gensalt
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


# ==================== Schemas ====================

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    """User registration schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ==================== Helper Functions ====================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = gensalt()
    return hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> dict:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": int(expire.timestamp())
        }
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )


def verify_token(credentials: HTTPAuthCredentials) -> dict:
    """Verify JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {"user_id": user_id, "payload": payload}
    except JWTError as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ==================== Routes ====================

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user.
    
    - **email**: User email address
    - **username**: Unique username
    - **password**: Password (min 8 characters)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    try:
        # TODO: Check if user already exists in MongoDB
        # user_exists = await db.users.find_one({"email": request.email})
        # if user_exists:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Email already registered"
        #     )
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Create user document
        user_data = {
            "email": request.email,
            "username": request.username,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # TODO: Insert into MongoDB
        # result = await db.users.insert_one(user_data)
        # user_id = str(result.inserted_id)
        
        user_id = "temp_user_id"  # Placeholder
        
        # Create tokens
        token_data = create_access_token(user_id)
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=token_data["expires_in"],
            user={
                "id": user_id,
                "email": request.email,
                "username": request.username
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login user and return JWT token.
    
    - **email**: User email address
    - **password**: User password
    """
    try:
        # TODO: Fetch user from MongoDB
        # user = await db.users.find_one({"email": request.email})
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid email or password"
        #     )
        
        # Verify password
        # if not verify_password(request.password, user["hashed_password"]):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid email or password"
        #     )
        
        user_id = "temp_user_id"  # Placeholder
        user_email = request.email  # Placeholder
        
        # Update last login
        # TODO: await db.users.update_one({"_id": user_id}, {"$set": {"last_login": datetime.utcnow()}})
        
        # Create token
        token_data = create_access_token(user_id)
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=token_data["expires_in"],
            user={
                "id": user_id,
                "email": user_email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/me")
async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """
    Get current authenticated user.
    """
    try:
        token_data = verify_token(credentials)
        user_id = token_data["user_id"]
        
        # TODO: Fetch user from MongoDB
        # user = await db.users.find_one({"_id": user_id})
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="User not found"
        #     )
        
        return {
            "id": user_id,
            "email": "user@example.com",
            "username": "username"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.post("/logout")
async def logout(credentials: HTTPAuthCredentials = Depends(security)):
    """
    Logout user (client should discard token).
    """
    return {"message": "Logged out successfully", "status": "success"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthCredentials = Depends(security)
):
    """
    Change user password.
    """
    try:
        token_data = verify_token(credentials)
        user_id = token_data["user_id"]
        
        # TODO: Fetch user from MongoDB
        # user = await db.users.find_one({"_id": user_id})
        # if not verify_password(request.current_password, user["hashed_password"]):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Current password is incorrect"
        #     )
        
        # Hash new password and update
        # new_hashed = hash_password(request.new_password)
        # await db.users.update_one({"_id": user_id}, {"$set": {"hashed_password": new_hashed}})
        
        return {"message": "Password changed successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
