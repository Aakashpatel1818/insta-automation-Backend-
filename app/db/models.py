"""Database models for Instagram Automation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== User Models ====================

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, max_length=128)


class User(UserBase):
    """User model with database fields."""
    id: Optional[str] = Field(None, alias="_id")
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    subscription_tier: str = "free"
    
    class Config:
        populate_by_name = True


# ==================== Rule Models ====================

class RuleType(str, Enum):
    """Types of automation rules."""
    COMMENT = "comment"
    DM = "dm"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"


class RuleBase(BaseModel):
    """Base rule model."""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    rule_type: RuleType
    trigger_keywords: List[str] = Field(default_factory=list)
    action_message: str
    is_case_sensitive: bool = False


class Rule(RuleBase):
    """Rule model with database fields."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    instagram_account_id: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# ==================== Log Models ====================

class LogType(str, Enum):
    """Types of logs."""
    COMMENT = "comment"
    DM = "dm"
    FOLLOW = "follow"
    ERROR = "error"


class LogStatus(str, Enum):
    """Log status."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class Log(BaseModel):
    """Log model."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    rule_id: Optional[str] = None
    log_type: LogType
    status: LogStatus
    message: str
    target_username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# ==================== Response Models ====================

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    status: str = "success"
    data: Optional[Dict[str, Any]] = None
