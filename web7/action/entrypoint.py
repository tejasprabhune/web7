import os
import dotenv
from pprint import pprint
import asyncio
from letta_client import (
    LlmConfig,
    AsyncLetta,
    MessageCreate,
    TextContent,
    AddMcpServerRequest,
    SseServerConfig,
)

from letta_client import Letta

dotenv.load_dotenv()

# Connect to Letta server
client = Letta(token=os.getenv("LETTA_API_KEY"))

# Use the "everything" mcp server:
# https://github.com/modelcontextprotocol/servers/tree/main/src/everything
mcp_server_name = "web7_notion"
mcp_tool_name = "NOTION_SEARCH_NOTION_PAGE"

# List all McpTool belonging to the "everything" mcp server.
mcp_tools = client.tools.list_mcp_tools_by_server(
    mcp_server_name=mcp_server_name,
)
for tool in mcp_tools:
    pprint(tool.name)
    print()

mcp_tool = client.tools.add_mcp_tool(
    mcp_server_name=mcp_server_name, mcp_tool_name=mcp_tool_name
)

agent_id = "agent-eba622c8-4ab9-49db-8c66-20e83f4fb4f7"
client.agents.tools.attach(agent_id=agent_id, tool_id=mcp_tool.id)

mcp_tools = client.agents.tools.list(agent_id=agent_id)

for tool in mcp_tools:
    pprint(tool.name)
    print()

# Ask the agent to call the tool.
response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[
        {"role": "user", "content": "Search all notion pages for `hi`"},
    ],
)
for message in response.messages:
    print(message)
