from qdrant_client import AsyncQdrantClient, models
import csv
from uuid import uuid4
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import List, Optional
from ..database_server.models import SearchResponse, MCPResponse, TransportType, SearchQuery

load_dotenv() 

class QdrantVectorDb:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url="https://34b705cd-636f-4f05-a4ce-440d4a8cbc10.us-west-1-0.aws.cloud.qdrant.io:6333", 
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.mcp_collection_name = "mcp_servers"
    
    async def search(self, search_query: SearchQuery) -> SearchResponse:
        query = search_query.query
        k = search_query.k
        try:
            query_vector = self.encoder.encode(query).tolist()

            search_result = await self.client.search(
                collection_name=self.mcp_collection_name,
                query_vector=query_vector,
                limit=k,
                with_payload=True
            )

            print("SEARCH RESULT: ", search_result)
            
            results = [MCPResponse(name=point.payload["name"], transport=TransportType.STREAMABLE_HTTP, url=point.payload["mcp_server_link"]) for point in search_result]
            
            return SearchResponse(
                success=True,
                query=query,
                servers=results
            )
        except Exception as e:
            print(f"An error occurred during search: {e}")
            return SearchResponse(
                success=False,
                query=query,
                servers=[]
            )
        
    async def health_check(self):
        try:
            await self.client.get_collections()
            return {"status": "healthy", "database": "qdrant-connected"}
        except Exception as e:
            return {"status": "unhealthy", "database": "qdrant-unreachable", "error": str(e)}

    async def create_collection(self, collection_name: str):
        await self.client.create_collection(
            collection_name,
            vectors_config=models.VectorParams(
                size=self.encoder.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
        )
    
    async def delete_collection(self, collection_name: str):
        await self.client.delete_collection(collection_name)

    async def upload_to_collection(self, payload: list, collection_name: str, vector_field: str="description"):
        points_to_upload = [
            models.PointStruct(
                id=str(uuid4()),
                vector=self.encoder.encode(doc[vector_field]).tolist(), 
                payload=doc
            )
            for doc in payload
        ]
        
        await self.client.upload_points(
            collection_name=collection_name,
            points=points_to_upload,
        )

    async def get_collection(self, collection_name: str):
        return await self.client.get_collection(collection_name)