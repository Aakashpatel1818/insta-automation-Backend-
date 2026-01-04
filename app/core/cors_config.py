"""CORS Configuration for production and development."""

import os
from typing import List


class CORSConfig:
    """CORS configuration management."""
    
    # Development origins
    DEV_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Production origins (from environment)
    @staticmethod
    def get_allowed_origins() -> List[str]:
        """Get allowed CORS origins based on environment."""
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        if env == "production":
            # Load from environment variable in production
            allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
            if not allowed_origins:
                raise ValueError(
                    "ALLOWED_ORIGINS environment variable must be set in production"
                )
            return [origin.strip() for origin in allowed_origins.split(",")]
        
        # Development defaults
        return CORSConfig.DEV_ORIGINS
    
    # CORS settings
    ALLOW_CREDENTIALS = True
    ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ]
    EXPOSE_HEADERS = ["Content-Length", "X-Total-Count"]
    MAX_AGE = 3600  # 1 hour


def validate_cors_config():
    """Validate CORS configuration at startup."""
    origins = CORSConfig.get_allowed_origins()
    if not origins:
        raise ValueError("No CORS origins configured")
    
    print(f"✅ CORS Configuration: {len(origins)} origin(s) allowed")
    return origins
