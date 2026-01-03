"""Main FastAPI application."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.routes import auth, rules, webhooks, logs, instagram

# Load environment variables from .env (if present)
load_dotenv()

# Setup logging using settings
logger = setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting Instagram Automation Pro API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Server: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logger.info(f"Database: {settings.MONGODB_DB_NAME}")
    logger.info(f"Instagram configured: {settings.instagram_configured}")
    logger.info(f"JWT configured: {settings.jwt_configured}")

    # TODO: Add real MongoDB connection check here if needed
    logger.info("✅ (Stub) Connected to MongoDB")

    yield

    # Shutdown
    logger.info("🛑 Shutting down API")
    # TODO: Close DB connections here
    logger.info("✅ (Stub) Disconnected from MongoDB")


app = FastAPI(
    title=settings.APP_NAME,
    description="Professional Instagram DM & Comment Automation API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse(
        {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "status": "running",
        }
    )


@app.get("/health")
async def health_check():
    """Basic health check."""
    return JSONResponse(
        {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
        }
    )


# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules Management"])
app.include_router(webhooks.router, prefix="/api/webhook", tags=["Webhooks"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs & Analytics"])
app.include_router(instagram.router)   # ✅ ONLY THIS


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Uvicorn at {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
