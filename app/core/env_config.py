"""Environment configuration loader."""

import os
from typing import Optional


class EnvConfig:
    """Environment variable configuration."""
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Instagram Automation Pro")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "instagram_automation")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Instagram API
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    INSTAGRAM_API_VERSION: str = os.getenv("INSTAGRAM_API_VERSION", "v18.0")
    
    # CORS
    ALLOWED_ORIGINS: Optional[str] = os.getenv("ALLOWED_ORIGINS")
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: str = os.getenv(
        "CORS_ALLOW_METHODS",
        "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    )
    CORS_ALLOW_HEADERS: str = os.getenv("CORS_ALLOW_HEADERS", "*")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    @classmethod
    def validate(cls) -> dict:
        """Validate critical configuration at startup."""
        errors = []
        warnings = []
        
        # Critical checks
        if cls.ENVIRONMENT == "production":
            if not cls.ALLOWED_ORIGINS:
                errors.append(
                    "ALLOWED_ORIGINS must be set in production environment"
                )
            
            if cls.JWT_SECRET_KEY == "your-secret-key-change-this":
                errors.append(
                    "JWT_SECRET_KEY must be changed from default in production"
                )
            
            if cls.DEBUG:
                warnings.append("DEBUG mode should be disabled in production")
        
        # MongoDB URL check
        if not cls.MONGODB_URL.startswith(("mongodb://", "mongodb+srv://")):
            errors.append("Invalid MONGODB_URL format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    @classmethod
    def get_settings(cls) -> dict:
        """Get all configuration as dictionary."""
        return {
            "server": {
                "host": cls.SERVER_HOST,
                "port": cls.SERVER_PORT,
                "debug": cls.DEBUG,
                "environment": cls.ENVIRONMENT,
            },
            "app": {
                "name": cls.APP_NAME,
                "version": cls.APP_VERSION,
            },
            "database": {
                "url": cls.MONGODB_URL.replace(
                    cls.MONGODB_URL.split("@")[0] if "@" in cls.MONGODB_URL else "",
                    "***"
                ),
                "name": cls.MONGODB_DB_NAME,
            },
            "jwt": {
                "algorithm": cls.JWT_ALGORITHM,
                "expiration_hours": cls.JWT_EXPIRATION_HOURS,
            },
        }
