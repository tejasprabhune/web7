import asyncio
import dotenv
from dataclasses import dataclass
import json
import os
import requests
from typing import Self

from letta_client import AsyncLetta, StreamableHttpServerConfig, Tool, SseServerConfig

from mcp.server.fastmcp import FastMCP

from ..search.vector_service import search_vectors

dotenv.load_dotenv()

mcp = FastMCP("search", stateless_http=True)
mcp.settings.port = 3001

client = AsyncLetta(token=os.getenv("LETTA_API_KEY"))
system_tools = [
    "tool-049053cc-0d04-4b2a-895b-68abfb46995e",  # send_message
    "tool-0c6f958b-61aa-4bb3-8bde-8ce836af9a77",  # core_memory_replace
    "tool-33317e3c-5b0d-489f-a8c2-94aa44e5d3dc",  # conversation_search
    "tool-718a6c47-9f7e-4f37-ab45-ea0a0cfbcc28",  # archival_memory_insert
    "tool-8ee5bbaf-397f-4132-8dc9-17c926adbdeb",  # core_memory_append
    "tool-9d63519f-409b-4a3b-bd07-36115c93d3e9",  # run_code
    "tool-ac00b505-d12d-4c4c-8e2b-98cf24b41cd1",  # archival_memory_search
    "tool-ee39ac08-1c08-4dcf-9b0d-c3f6e086c27d",  # web_search
]


@dataclass
class McpServer:
    name: str
    transport: str
    url: str
    image_url: str
    authentication: str


@dataclass
class McpResponse:
    success: bool
    query: str
    servers: list[McpServer]

    def from_dict(data: dict) -> Self:
        return McpResponse(
            data["success"],
            data["query"],
            servers=[McpServer(**server) for server in data["servers"]],
        )


async def detach_tools(agent_id: str) -> None:
    attached_tools: list[Tool] = await client.agents.tools.list(agent_id=agent_id)

    detach_tasks = []
    for attached_tool in attached_tools:
        if (
            attached_tool.id not in system_tools
        ):  # and attached_tool.name != "mcp_search":
            print("detaching:", attached_tool.name)
            detach_tasks.append(
                asyncio.create_task(
                    client.agents.tools.detach(
                        agent_id=agent_id, tool_id=attached_tool.id
                    )
                )
            )

    await asyncio.gather(*detach_tasks, return_exceptions=True)


async def add_tool(agent_id: str, mcp_server_name: str, mcp_tool_name: str):
    tool = await client.tools.add_mcp_tool(
        mcp_server_name=mcp_server_name,
        mcp_tool_name=mcp_tool_name,
    )
    await client.agents.tools.attach(agent_id=agent_id, tool_id=tool.id)


async def attach_tools(agent_id: str, mcp_server_name: str):
    available_tools: list[Tool] = await client.tools.list_mcp_tools_by_server(
        mcp_server_name
    )

    attach_tasks = []
    for available_tool in available_tools:
        print("adding mcp server tool:", available_tool.name)
        attach_tasks.append(
            asyncio.create_task(
                add_tool(agent_id, mcp_server_name, available_tool.name)
            )
        )

    await asyncio.gather(*attach_tasks, return_exceptions=True)


async def add_mcp_server(mcp_server_name: str, mcp_server_url: str):
    current_mcp_servers = await client.tools.list_mcp_servers()
    print(current_mcp_servers)

    if mcp_server_name not in current_mcp_servers:
        print("adding mcp server:", mcp_server_name)
        response = await client.tools.add_mcp_server(
            request=SseServerConfig(
                server_name=mcp_server_name,
                server_url=mcp_server_url,
            )
        )
        print(response)


async def _mcp_search(agent_id: str, query: str, k: int) -> int:
    """
    Retrieve MCP servers to inject into this agent for a given query.
    For example, if I want to send an email, I will retrieve the Gmail MCP servers
    and inject it into this agent ID for you.

    agent_id: letta agent id for
    query: str - prompt query for searching relevant MCP servers
    k: int - number of MCP servers to return
    """
    # response = requests.get(
    #     url=f"{os.getenv('SEARCH_ENDPOINT')}/search", params={"query": query, "k": k}
    # )

    # print(response.json())

    response = await search_vectors(query, k)
    print(response.json())

    mcp_response: McpResponse = McpResponse.from_dict(json.loads(response.json()))

    await detach_tools(agent_id)

    mcp_server_img_url = ""
    for server in mcp_response.servers:
        await add_mcp_server(server.name, server.url)
        await attach_tools(agent_id, server.name)
        mcp_server_img_url = server.image_url

    return mcp_server_img_url


@mcp.tool()
async def mcp_search(agent_id: str, query: str, k: int) -> int:
    print("agent_id:", agent_id)
    print("query:", query)
    print("k:", k)
    mcp_server_img_url = await _mcp_search(agent_id, query, k)

    return {"status": "success", "mcp_server_img_url": mcp_server_img_url}


async def main():
    response = requests.get(
        url=f"{os.getenv('SEARCH_ENDPOINT')}/search",
        params={"query": "send email", "k": 2},
    )

    mcp_response: McpResponse = McpResponse.from_dict(response.json())
    print(mcp_response)

    agent_id = "agent-167487e1-cd1c-4b24-8f43-c84012ded7f9"
    mcp_server_name = "web7_notion"
    mcp_server_url = "https://mcp.composio.dev/composio/server/2209a624-d742-49c5-9eb0-739d6ff86cff/mcp"
    await add_mcp_server(
        mcp_server_name,
        mcp_server_url,
    )

    await attach_tools(agent_id=agent_id, mcp_server_name=mcp_server_name)

    await detach_tools(agent_id=agent_id)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
