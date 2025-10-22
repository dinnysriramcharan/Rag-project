#!/usr/bin/env python3
"""
Production startup script for the RAG Chatbot API
"""
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (required for most cloud platforms)
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=port,
        reload=False,  # Disable reload in production
        workers=1,  # Single worker for serverless
        log_level="info"
    )
