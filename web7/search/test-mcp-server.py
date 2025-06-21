import os
import requests

api_key = os.environ.get("ANTHROPIC_API_KEY")
headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key,
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "mcp-client-2025-04-04",
}

body = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "What tools do you have available?"}],
    "mcp_servers": [
      {
        "type": "url",
        "url": "https://example-server.modelcontextprotocol.io/sse",
        "name": "example-mcp",
        "authorization_token": "YOUR_TOKEN"
      }
    ]
  }

requests.get("https://api.anthropic.com/v1/messages",
    data=body,
    headers=headers
)