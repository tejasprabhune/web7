from qdrant_client import QdrantClient, models
import csv
from uuid import uuid4
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv() 

class QdrantVectorDb:
    def __init__(self):
        self.client = QdrantClient(
            url="https://34b705cd-636f-4f05-a4ce-440d4a8cbc10.us-west-1-0.aws.cloud.qdrant.io:6333", 
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.mcp_collection_name = "mcp_servers"
    
    def query_points(self, query: str, limit: int=2):
        search_result = self.client.query_points(
            collection_name=self.mcp_collection_name,
            query=self.encoder.encode(query),
            limit=limit
        ).points
        results = [result.payload for result in search_result]
        return results

    def create_collection(self, collection_name: str):
        self.client.create_collection(
            collection_name,
            vectors_config=models.VectorParams(
                size=self.encoder.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
        )
        return self.client.create_collection(collection_name)
    
    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name)

    def upload_to_collection(self, payload: list, collection_name: str, vector_field: str="description"):
        self.client.upload_points(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=idx, vector=self.encoder.encode(doc[vector_field]).tolist(), payload=doc
                )
                for idx, doc in enumerate(payload)
            ],
        )

    def get_collection(self, collection_name: str):
        return self.client.get_collection(collection_name)

qdrant_vector_db = QdrantVectorDb()
print(qdrant_vector_db.query_points("send email"))