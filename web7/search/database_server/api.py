from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import List, Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv
from ..qdrant_vector_search.qdrant_client import QdrantVectorDb
from .models import SearchQuery, SearchResponse

load_dotenv()

app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0"
)

# Add this endpoint to handle favicon requests
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return RedirectResponse(url="about:blank")

vector_service = QdrantVectorDb()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_health = await vector_service.health_check()
    return {
        "status": "healthy",
        "service": "web7-vector-search",
        "version": "1.0.0",
        "database": db_health
    }

# GET endpoint for simple queries
@app.get("/search", response_model=SearchResponse)
async def search_vectors_get(
    query: str = Query(..., description="Search query string", min_length=1, max_length=1000),
    k: int = Query(default=1, description="Number of results", ge=1, le=100)
):
    """
    GET endpoint for vector search.
    """
    search_query = SearchQuery(query=query, k=k)
    try:
        result = await vector_service.search(search_query=search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    # Run the FastAPI server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 