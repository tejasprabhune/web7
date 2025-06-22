from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List, Dict, Any, Optional
import uvicorn
import os
from enum import Enum
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Self
from .search.qdrant_vector_search.qdrant_client import QdrantVectorDb
from .models import (
    SearchQuery,
    SearchResponse,
    UserQueryRequest,
    UserQueryRequestWithId,
    WorkflowSession,
    WorkflowStatus,
    Step,
    StepStatus,
)
from datetime import datetime
import uuid
import asyncio
import time
from letta_client import LlmConfig, AsyncLetta, StreamableHttpServerConfig
from web7.action.agent import generate_task_list, accomplish_task

load_dotenv()

client = AsyncLetta(token=os.getenv("LETTA_API_KEY"))
app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0",
)


workflow_sessions: Dict[str, WorkflowSession] = {}


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


@app.post("/user-query")
async def submit_query(request: UserQueryRequest, background_tasks: BackgroundTasks):
    """Submit query and start processing in background"""
    agent_id = await create_agent()
    session = WorkflowSession(agent_id, request.query)
    workflow_sessions[agent_id] = session

    background_tasks.add_task(process_workflow, agent_id, request.query)

    return {
        "agent_id": agent_id,
        "status": "initiated",
        "message": "Workflow started successfully",
    }


@app.post("/user-query-id")
async def submit_query_with_id(
    request: UserQueryRequestWithId, background_tasks: BackgroundTasks
):
    """Submit query and start processing in background"""
    session = WorkflowSession(request.agent_id, request.query)
    workflow_sessions[request.agent_id] = session

    background_tasks.add_task(process_workflow, request.agent_id, request.query)

    return {
        "agent_id": request.agent_id,
        "status": "initiated",
        "message": "Workflow started successfully",
    }


@app.get("/workflow/{agent_id}")
async def get_workflow_status(agent_id: str):
    """Get current workflow status - Frontend polls this endpoint"""
    if agent_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Agent not found")

    session = workflow_sessions[agent_id]
    return session.to_dict()


async def process_workflow(agent_id: str):
    """Main workflow processing logic - customize this for your LLM"""
    session = workflow_sessions[agent_id]

    try:
        session.status = WorkflowStatus.IN_PROGRESS

        # Define your workflow steps
        workflow_steps: list[str] = await generate_task_list(
            session.agent_id, session.query
        )

        print("workflow steps:", workflow_steps)

        total_steps = len(workflow_steps)

        for i, step in enumerate(workflow_steps):
            await accomplish_task(session, step, i)
            session.current_step = i
            session.set_progress(int((i / total_steps) * 100))

        session.status = WorkflowStatus.SUCCEEDED
        session.set_progress(100)

    except Exception as e:
        session.status = WorkflowStatus.FAILED
        session.error_message = str(e)
        # Mark current step as failed if it exists
        if session.steps and session.current_step < len(session.steps):
            current_step = session.steps[session.current_step]
            session.update_step(
                current_step.step_id,
                status=StepStatus.FAILED,
                details={"error": str(e)},
            )


vector_service = QdrantVectorDb()


# GET endpoint for simple queries
@app.get("/search", response_model=SearchResponse)
async def search_vectors_get(
    query: str = Query(
        ..., description="Search query string", min_length=1, max_length=1000
    ),
    k: int = Query(default=1, description="Number of results", ge=1, le=100),
):
    """
    GET endpoint for vector search.
    """
    search_query = SearchQuery(query=query, k=k)
    try:
        result = await vector_service.search(search_query=search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


async def main():
    await init_letta()
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("api:app", host=host, port=port, reload=True, log_level="info")


if __name__ == "__main__":
    asyncio.run(main())
