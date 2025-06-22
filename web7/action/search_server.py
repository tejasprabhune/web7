from fastapi import FastAPI, Query
import uvicorn

app = FastAPI(
    title="Search API",
    description="A simple search API with query, and key parameters",
)


@app.get("/search")
async def search(
    query: str = Query(..., description="Search query parameter"),
    k: str = Query(..., description="API key parameter"),
):
    return {
        "success": True,
        "query": query,
        "servers": [
            {
                "name": "web7_notion",
                "transport": "streamable-http",
                "url": "https://mcp.composio.dev/composio/server/2209a624-d742-49c5-9eb0-739d6ff86cff/mcp",
                "authentication": "",
            },
            {
                "name": "web7_gmail",
                "transport": "streamable-http",
                "url": "https://mcp.composio.dev/composio/server/7d3d4809-4766-45e3-92f2-7c646c11b1cb/mcp?include_composio_helper_actions=true",
                "authentication": "",
            },
        ],
    }


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Search API is running! Use /search endpoint with query, and key parameters."
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
