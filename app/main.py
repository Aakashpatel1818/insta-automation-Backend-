"""Main FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

# Import routes
from app.api.routes import auth, rules, logs, instagram, webhooks


# ==================== Logging Setup ====================

def setup_logging():
    """Configure application logging."""
    log_level = logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


setup_logging()
logger = logging.getLogger(__name__)


# ==================== MongoDB Connection ====================

class Database:
    """Database connection manager."""
    client = None
    db = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            db_name = os.getenv("MONGODB_DB_NAME", "instagram_automation")
            
            cls.client = AsyncIOMotorClient(mongo_url)
            cls.db = cls.client[db_name]
            
            # Verify connection
            await cls.db.command("ping")
            logger.info("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        try:
            if cls.client:
                cls.client.close()
                logger.info("✅ MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {str(e)}")


# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("🚀 Starting Instagram Automation Backend")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    try:
        await Database.connect_db()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Instagram Automation Backend")
    await Database.close_db()


# ==================== FastAPI Application ====================

app = FastAPI(
    title="Instagram Automation Pro API",
    description="Automate your Instagram interactions with rules and workflows",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ==================== CORS Configuration ====================

# Get allowed origins from environment
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
)

# Parse and clean origins
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Log CORS configuration
logger.info(f"✅ CORS Configuration: {len(allowed_origins)} origin(s) allowed")
for origin in allowed_origins:
    logger.info(f"   - {origin}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,
)


# ==================== Error Handling ====================

class ErrorResponse:
    """Error response formatter."""
    @staticmethod
    def format(status_code: int, detail: str, error_type: str = "error") -> dict:
        return {
            "status": "error",
            "error_type": error_type,
            "detail": detail,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_type": "validation_error",
            "detail": "Validation failed",
            "errors": errors,
            "status_code": 422,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.format(
            500,
            "Internal server error",
            "server_error"
        )
    )


# ==================== Request Logging Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.utcnow()
    
    # Log request details
    logger.debug(f"Request: {request.method} {request.url.path}")
    logger.debug(f"Origin: {request.headers.get('origin', 'No origin header')}")
    
    try:
        response = await call_next(request)
        
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"{request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Duration: {process_time:.3f}s"
        )
        raise


# ==================== Health Check ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Instagram Automation Pro API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Instagram Automation Pro API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


# ==================== Register Routes ====================

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    rules.router,
    prefix="/api/rules",
    tags=["Rules"],
)

app.include_router(
    logs.router,
    prefix="/api/logs",
    tags=["Logs & Analytics"],
)

app.include_router(
    instagram.router,
    prefix="/api/instagram",
    tags=["Instagram Integration"],
)

app.include_router(
    webhooks.router,
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )