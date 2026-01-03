"""
Application Configuration Management
Handles all environment variables with validation and defaults
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
from typing import List, Optional
import json
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with validation.
    Loads from environment variables or .env file.
    """

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    APP_NAME: str = "Instagram Automation Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============================================================================
    # SERVER SETTINGS
    # ============================================================================
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    RELOAD: bool = False  # Auto-reload on code changes (dev only)

    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "instagram_automation"
    MONGODB_TIMEOUT: int = 5000  # milliseconds

    # ============================================================================
    # INSTAGRAM API SETTINGS
    # ============================================================================
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_REDIRECT_URI: str = ""
    INSTAGRAM_WEBHOOK_VERIFY_TOKEN: str = ""
    INSTAGRAM_API_VERSION: str = "v18.0"
    INSTAGRAM_GRAPH_API_BASE_URL: str = "https://graph.instagram.com"

    # ============================================================================
    # JWT SETTINGS
    # ============================================================================
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============================================================================
    # CORS SETTINGS
    # ============================================================================
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ============================================================================
    # LOGGING SETTINGS
    # ============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, standard
    LOG_FILE: Optional[str] = None  # None = console only

    # ============================================================================
    # TIMEZONE
    # ============================================================================
    TIMEZONE: str = "Asia/Kolkata"

    # ============================================================================
    # MODEL CONFIGURATION
    # ============================================================================
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

    # ============================================================================
    # VALIDATORS
    # ============================================================================

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, v):
        """Convert string to boolean"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment is one of allowed values"""
        allowed = ["development", "staging", "production"]
        env = str(v).lower()
        if env not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got {env}")
        return env

    @field_validator("SERVER_PORT", mode="before")
    @classmethod
    def validate_port(cls, v):
        """Validate port is valid"""
        port = int(v) if isinstance(v, str) else v
        if not 1 <= port <= 65535:
            raise ValueError(f"SERVER_PORT must be between 1 and 65535, got {port}")
        return port

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def validate_origins(cls, v):
        """Parse ALLOWED_ORIGINS from JSON string or list"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(f"ALLOWED_ORIGINS must be valid JSON, got {v}")
        return v

    @field_validator("CORS_CREDENTIALS", mode="before")
    @classmethod
    def validate_cors_credentials(cls, v):
        """Convert string to boolean"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level = str(v).upper()
        if level not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got {level}")
        return level

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    @classmethod
    def validate_token_expire(cls, v):
        """Validate token expiration"""
        minutes = int(v) if isinstance(v, str) else v
        if minutes < 1:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be >= 1")
        return minutes

    @field_validator("BCRYPT_ROUNDS", mode="before")
    @classmethod
    def validate_bcrypt_rounds(cls, v):
        """Validate bcrypt rounds"""
        rounds = int(v) if isinstance(v, str) else v
        if not 4 <= rounds <= 31:
            raise ValueError("BCRYPT_ROUNDS must be between 4 and 31")
        return rounds

    # ============================================================================
    # PROPERTIES
    # ============================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.ENVIRONMENT == "testing"

    @property
    def instagram_configured(self) -> bool:
        """Check if Instagram API is properly configured"""
        required_fields = [
            self.INSTAGRAM_APP_ID,
            self.INSTAGRAM_APP_SECRET,
            self.INSTAGRAM_REDIRECT_URI,
            self.INSTAGRAM_WEBHOOK_VERIFY_TOKEN,
        ]
        return all(required_fields)

    @property
    def jwt_configured(self) -> bool:
        """Check if JWT is properly configured"""
        return (
            self.JWT_SECRET_KEY != "your-secret-key-change-this-in-production"
            and len(self.JWT_SECRET_KEY) >= 32
        )

    # ============================================================================
    # METHODS
    # ============================================================================

    def get_instagram_base_url(self) -> str:
        """Get Instagram Graph API base URL with version"""
        return f"{self.INSTAGRAM_GRAPH_API_BASE_URL}/{self.INSTAGRAM_API_VERSION}"

    def get_database_url(self) -> str:
        """Get MongoDB connection URL"""
        return self.MONGODB_URI

    def get_database_name(self) -> str:
        """Get database name"""
        return self.MONGODB_DB_NAME


# ============================================================================
# LOAD SETTINGS
# ============================================================================

def load_settings() -> Settings:
    """
    Load settings from environment and validate.
    Raises ValidationError if configuration is invalid.
    """
    try:
        settings = Settings()
        
        # Log loaded configuration (mask sensitive data)
        if settings.DEBUG:
            print("✅ Configuration loaded successfully")
            print(f"   Environment: {settings.ENVIRONMENT}")
            print(f"   Debug: {settings.DEBUG}")
            print(f"   Server: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
            print(f"   Database: {settings.MONGODB_DB_NAME}")
            print(f"   Instagram API: {settings.instagram_configured}")
            print(f"   JWT Configured: {settings.jwt_configured}")
        
        # Warnings for production
        if settings.is_production:
            if not settings.jwt_configured:
                raise ValueError(
                    "❌ JWT_SECRET_KEY not properly configured for production. "
                    "Must be at least 32 characters and different from default."
                )
            if not settings.instagram_configured:
                print(
                    "⚠️  WARNING: Instagram API not fully configured. "
                    "Some features will not work."
                )
        
        return settings
    except ValidationError as e:
        print("❌ Configuration validation failed:")
        for error in e.errors():
            print(f"   - {error['loc'][0]}: {error['msg']}")
        raise


# Create global settings instance
try:
    settings = load_settings()
except ValidationError as e:
    print("Failed to load settings. Exiting...")
    raise


# ============================================================================
# EXPORT
# ============================================================================
__all__ = ["settings", "Settings", "load_settings"]