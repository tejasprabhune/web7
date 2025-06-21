#!/usr/bin/env python3
"""
Script to run the Web7 Vector Search API server.
"""

import sys
import os
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting Web7 Vector Search API server...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    print("Press Ctrl+C to stop the server")
    
    # Run the server with import string for reload support
    uvicorn.run(
        "web7.search.database_server.api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
