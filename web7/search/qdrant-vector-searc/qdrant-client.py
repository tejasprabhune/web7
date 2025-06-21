from qdrant_client import QdrantClient, models
import os
from qdrant_client.models import Distance, VectorParams

api_key = os.environ.get("QDRANT_API_KEY")

client = QdrantClient("https://34b705cd-636f-4f05-a4ce-440d4a8cbc10.us-west-1-0.aws.cloud.qdrant.io:6333", api_key=api_key)

model_name = "sentence-transformers/all-MiniLM-L6-v2"

payload = [
    {"document": "Qdrant has Langchain integrations", "source": "Langchain-docs", },
    {"document": "Qdrant also has Llama Index integrations", "source": "LlamaIndex-docs"},
]
docs = [models.Document(text=data["document"], model=model_name) for data in payload]
ids = [42, 2]

client.create_collection(
    "demo_collection",
    vectors_config=models.VectorParams(
        size=client.get_embedding_size(model_name), distance=models.Distance.COSINE)
)

client.upload_collection(
    collection_name="demo_collection",
    vectors=docs,
    ids=ids,
    payload=payload,
)

search_result = client.query_points(
    collection_name="demo_collection",
    query=models.Document(text="This is a query document", model=model_name)
).points
print(search_result)