"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from app.api.routes import auth, rules, webhooks, logs
from app.core.config import settings

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    print("✅ Connected to MongoDB")
    yield
    # Shutdown
    print("🛑 Shutting down...")
    print("✅ Disconnected from MongoDB")

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Automation Pro API",
    description="Professional Instagram DM & Comment Automation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Root endpoint
@app.get("/")
async def root():
    return JSONResponse({
        "message": "Welcome to Instagram Automation Pro API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    })

# Health check
@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    })

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules Management"])
app.include_router(webhooks.router, prefix="/api/webhook", tags=["Webhooks"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs & Analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )