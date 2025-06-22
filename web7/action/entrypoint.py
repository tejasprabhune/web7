from fastapi import FastAPI

import os
import dotenv
from pprint import pprint
import asyncio
from letta_client import LlmConfig, AsyncLetta, StreamableHttpServerConfig

from .interface_search import attach_tools

dotenv.load_dotenv()
client = AsyncLetta(token=os.getenv("LETTA_API_KEY"))
app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0",
)
running_tasks = set()


async def init_letta():
    await client.tools.add_mcp_server(
        request=StreamableHttpServerConfig(
            server_name="search", server_url=os.getenv("SEARCH_MCP_ENDPOINT")
        )
    )


async def create_agent(tool_id: int):
    search_tool = await client.tools.add_mcp_tool("search", "mcp_search")
    agent = await client.agents.create(
        model="anthropic/claude-sonnet-4-20250514",
        embedding="openai/text-embedding-3-small",
        memory_blocks=[
            {"label": "human", "value": ""},
            {
                "label": "persona",
                "value": (
                    "I am an AI assistant agent tailored towards executing"
                    "workflows using tools to accomplish the user's task."
                ),
            },
        ],
    )
    await client.agents.tools.attach(agent.id, search_tool.id)

    return agent.id


async def _action_request(agent_id: int, prompt: str) -> str:
    # convert prompt to bigger prompt
    # convert bigger prompt to steps
    #
    pass


@app.post("/request_action")
async def request_action(prompt: str) -> str:
    agent_id = await create_agent()
    action_task = asyncio.create_task(_action_request(prompt))
    running_tasks.add(action_task)
    action_task.add_done_callback(lambda t: running_tasks.remove(t))

    return agent_id


async def main():
    await init_letta()


if __name__ == "__main__":
    pass
