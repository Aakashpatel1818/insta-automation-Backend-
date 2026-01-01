#!/usr/bin/env python
"""Run the FastAPI application"""

import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    debug = os.getenv("DEBUG", "True") == "True"
    
    print(f"🚀 Starting Instagram Automation Pro Backend")
    print(f"📍 Server: {host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )