import os
import requests

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("search", stateless_http=True)
mcp.settings.port = 3001


@mcp.tool()
def mcp_search(agent_id: int, q: str, k: int) -> int:
    """
    /search

    q: str - prompt query for searching relevant MCP servers
    k: int - number of MCP servers to return

    Returns:
    {
        "success": bool,
        "query": str,
        "results": [
            "<mcp-name>": {
                "transport": "streamable-http" | "sse" | "stdio",
                "url": str,
                "authentication": str
            }
        ]
    }
    """
    requests.get(os.getenv("SEARCH_ENDPOINT"))


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
