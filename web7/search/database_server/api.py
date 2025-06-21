from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv
from ..vector_service import MCPVectorDBService, VectorSearchParams
from .models import SearchQuery, SearchResponse

load_dotenv()

app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0"
)

vector_service = MCPVectorDBService()

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
    q: str = Query(..., description="Search query string", min_length=1, max_length=1000),
    k: int = Query(default=1, description="Number of results", ge=1, le=100)
):
    """
    GET endpoint for vector search.
    """
    search_query = SearchQuery(query=q, k=k)
    try:
        params = VectorSearchParams(query=search_query.query)
        result = await vector_service.search(params)
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