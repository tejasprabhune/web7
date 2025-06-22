from .qdrant_vector_search.qdrant_client import QdrantVectorDb
from ..models import SearchQuery
from fastapi import HTTPException

vector_service = QdrantVectorDb()


async def search_vectors(query: str, k: int):
    search_query = SearchQuery(query=query, k=k)
    try:
        result = await vector_service.search(search_query=search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
