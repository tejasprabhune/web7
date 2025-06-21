from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class SearchQuery(BaseModel):
    """Model for search query request."""
    query: str = Field(..., description="The search query string", min_length=1, max_length=1000)
    k: int = Field(default=1, description="The number of results to return", ge=1, le=100)

class TransportType(Enum):
    """The transport type."""
    STREAMABLE_HTTP = "streamable-http"
    SSE = "sse"
    STDIO = "stdio"

class MCPResponse(BaseModel):
    name: str = Field(..., description="The name of the MCP server")
    transport: TransportType = Field(..., description="The transport type")
    url: str = Field(..., description="The URL of the MCP server")
    authentication: Optional[str] = Field(default=None, description="The authentication token")

class SearchResponse(BaseModel):
    """Model for search response."""
    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The original query")
    servers: List[MCPResponse] = Field(..., description="List of search results") 