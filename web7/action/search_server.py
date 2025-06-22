from fastapi import FastAPI, Query
import uvicorn

app = FastAPI(
    title="Search API",
    description="A simple search API with agent_id, query, and key parameters",
)


@app.get("/search")
async def search(
    agent_id: str = Query(..., description="Agent ID parameter"),
    query: str = Query(..., description="Search query parameter"),
    key: str = Query(..., description="API key parameter"),
):
    static_response = f"Search completed successfully! Agent ID: {agent_id}, Query: '{query}', Key authenticated."

    return {
        "status": "success",
        "message": static_response,
        "parameters": {"agent_id": agent_id, "query": query, "key": key},
    }


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Search API is running! Use /search endpoint with agent_id, query, and key parameters."
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
