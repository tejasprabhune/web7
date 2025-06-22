#!/usr/bin/env python3
"""
Test client for the Web7 Vector Search API.
"""
import sys
import os

# This is the crucial part: Add the project root to the Python path
# so that the `web7` module can be found. This must be done BEFORE
# any imports from the `web7` package.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import asyncio
import httpx
import json
from typing import Dict, Any
from web7.search.database_server.models import SearchResponse, MCPResponse, TransportType

async def test_search():
    """Test the vector search endpoint."""
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic search
            query = "send email"
            print(f"🔍 Testing search with query: '{query}'...")
            response = await client.get(f"{base_url}/search", params={"query": query, "k": 2})
            
            if response.status_code == 200:
                print("✅ Search successful!")
                search_response = SearchResponse(**response.json())
                print(f"   Query: {search_response.query}")
                print(f"   Results: {search_response}")
            else:
                print(f"❌ Search failed with status: {response.status_code}")
                print(f"   Response: {response.text}")

            # Test health check
            print("\n🔍 Testing health check...")
            health_response = await client.get(f"{base_url}/health")
            if health_response.status_code == 200:
                 print("✅ Health check successful!")
                 print(f"   Response: {health_response.json()}")
            else:
                 print(f"❌ Health check failed with status: {health_response.status_code}")

    except httpx.ConnectError:
        print("\n" + "="*50)
        print("❌ CONNECTION FAILED")
        print("Could not connect to the server at http://localhost:8000.")
        print("\n❗️ Please start the server in a separate terminal before running the client:")
        print("   -> python scripts/run_server.py")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(test_search())
