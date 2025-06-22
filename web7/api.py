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
)
from datetime import datetime
import uuid
import asyncio
import time
from letta_client import LlmConfig, AsyncLetta, StreamableHttpServerConfig
from action.agent import generate_task_list

load_dotenv()

client = AsyncLetta(token=os.getenv("LETTA_API_KEY"))
app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0",
)


class WorkflowStatus(Enum):
    STARTED = 1
    IN_PROGRESS = 2
    FAILED = 3

    def from_str(status: str) -> Self:
        match status:
            case "started":
                return WorkflowStatus.STARTED
            case "in_progress":
                return WorkflowStatus.IN_PROGRESS
            case "failed":
                return WorkflowStatus.FAILED


class StepStatus(Enum):
    NOT_STARTED = 0
    STARTED = 1
    UPDATED = 2
    FAILED = 3

    def from_str(status: str) -> Self:
        match status:
            case "not_started":
                return StepStatus.NOT_STARTED
            case "started":
                return StepStatus.STARTED
            case "updated":
                return StepStatus.UPDATED
            case "failed":
                return StepStatus.FAILED


@dataclass
class Step:
    step_id: str
    action: str
    mcp_server: str
    status: StepStatus
    timestamp: str
    details: str
    duration: float

    def to_dict(self):
        """
        Serialize Step to a dictionary.
        """
        return {
            "step_id": self.step_id,
            "action": self.action,
            "mcp_server": self.mcp_server,
            "status": self.status.name.lower(),
            "timestamp": self.timestamp,
            "details": self.details,
            "duration": self.duration,
        }


class WorkflowSession:
    def __init__(self, agent_id: str, query: str):
        self.agent_id = agent_id
        self.query = query
        self.status = WorkflowStatus.STARTED
        self.steps: list[Step] = []
        self.current_step = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.progress_percentage = 0
        self.error_message = None

    def add_step(
        self,
        action: str,
        mcp_server: str,
        status: StepStatus = StepStatus.NOT_STARTED,
        details: str = None,
    ):
        step = Step(
            step_id=f"step_{len(self.steps) + 1}",
            action=action,
            mcp_server=mcp_server,
            status=status,
            details=details,
            timestamp=datetime.now().isoformat(),
            duration=None,
        )
        self.steps.append(step)
        self.updated_at = datetime.now()
        return step

    def update_step(
        self, step_id: str, status: str, details: dict = None, duration: float = None
    ):
        for step in self.steps:
            if step.step_id == step_id:
                step.status = status
                step.timestamp = datetime.now().isoformat()
                step.details = details
                if duration:
                    step.duration = duration
                break
        self.updated_at = datetime.now()

    def set_progress(self, percentage: int):
        self.progress_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.now()

    def to_dict(self):
        """
        Serialize WorkflowSession to a dictionary.
        """
        return {
            "agent_id": self.agent_id,
            "query": self.query,
            "status": self.status.name.lower(),
            "steps": [step.to_dict() for step in self.steps],
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress_percentage": self.progress_percentage,
            "error_message": self.error_message,
        }


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


async def process_workflow(session_id: str):
    """Main workflow processing logic - customize this for your LLM"""
    session = workflow_sessions[session_id]

    try:
        session.status = "processing"

        # Define your workflow steps
        workflow_steps = await generate_task_list(session.agent_id, session.query)

        total_steps = len(workflow_steps)

        for i, step_config in enumerate(workflow_steps):
            # Add step to session
            step = session.add_step(
                action=step_config["action"],
                mcp_server=step_config["mcp_server"],
                status="started",
                details={
                    "description": f"Starting {step_config['action'].replace('_', ' ')}"
                },
            )

            session.current_step = i
            session.set_progress(int((i / total_steps) * 100))

            start_time = time.time()

            # Simulate the actual work (replace with your LLM/MCP calls)
            await simulate_mcp_call(
                step_config["action"],
                step_config["mcp_server"],
                step_config["duration"],
            )

            duration = time.time() - start_time

            # Update step as completed
            session.update_step(
                step["step_id"],
                status="completed",
                details={
                    "description": f"Successfully completed {step_config['action'].replace('_', ' ')}",
                    "result": f"Processed by {step_config['mcp_server']}",
                },
                duration=duration,
            )

            session.set_progress(int(((i + 1) / total_steps) * 100))

        # Mark workflow as completed
        session.status = "completed"
        session.set_progress(100)

    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        # Mark current step as failed if it exists
        if session.steps and session.current_step < len(session.steps):
            current_step = session.steps[session.current_step]
            session.update_step(
                current_step["step_id"], status="failed", details={"error": str(e)}
            )


async def simulate_mcp_call(action: str, mcp_server: str, duration: int):
    """Simulate MCP server call - replace with actual implementation"""
    await asyncio.sleep(duration)

    # Here you would make actual calls to your LLM backend
    # Example:
    # if action == "analyze_query":
    #     result = await your_llm_client.analyze_query(...)
    # elif action == "connect_to_database":
    #     result = await your_mcp_client.connect_database(...)

    return {"status": "success", "action": action, "server": mcp_server}


@app.get("/")
async def serve_frontend():
    """Serve the simple HTML frontend"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Workflow Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .query-form { margin-bottom: 30px; }
            .query-input { width: 70%; padding: 10px; font-size: 16px; }
            .submit-btn { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            .workflow-container { margin-top: 20px; }
            .step { padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ddd; }
            .step.started { border-left-color: #007bff; background: #e7f3ff; }
            .step.completed { border-left-color: #28a745; background: #e8f5e9; }
            .step.failed { border-left-color: #dc3545; background: #ffebee; }
            .progress-bar { width: 100%; background: #f0f0f0; border-radius: 4px; margin: 20px 0; }
            .progress-fill { height: 20px; background: #007bff; border-radius: 4px; transition: width 0.3s; }
            .loading { display: none; }
            .error { color: #dc3545; background: #ffebee; padding: 10px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>MCP Workflow Dashboard</h1>
        
        <div class="query-form">
            <input type="text" id="queryInput" class="query-input" placeholder="Enter your query..." />
            <button onclick="submitQuery()" class="submit-btn">Submit Query</button>
        </div>
        
        <div id="loading" class="loading">Processing your query...</div>
        <div id="error" class="error" style="display: none;"></div>
        
        <div id="workflowContainer" class="workflow-container" style="display: none;">
            <h2>Query: <span id="currentQuery"></span></h2>
            
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%;"></div>
            </div>
            <p>Progress: <span id="progressText">0%</span></p>
            
            <div id="workflowSteps"></div>
        </div>

        <script>
            let currentSessionId = null;
            let pollingInterval = null;

            async function submitQuery() {
                const query = document.getElementById('queryInput').value.trim();
                if (!query) return;

                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('workflowContainer').style.display = 'none';
                document.getElementById('error').style.display = 'none';

                try {
                    const response = await fetch('/user-query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    if (!response.ok) throw new Error('Failed to submit query');

                    const result = await response.json();
                    currentSessionId = result.session_id;
                    
                    // Start polling for updates
                    startPolling();
                    
                } catch (error) {
                    showError('Failed to submit query: ' + error.message);
                }
            }

            function startPolling() {
                if (pollingInterval) clearInterval(pollingInterval);
                
                pollingInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`/workflow/${currentSessionId}`);
                        if (!response.ok) throw new Error('Failed to get workflow status');
                        
                        const workflow = await response.json();
                        updateWorkflowDisplay(workflow);
                        
                        // Stop polling if completed or failed
                        if (workflow.status === 'completed' || workflow.status === 'failed') {
                            clearInterval(pollingInterval);
                        }
                        
                    } catch (error) {
                        showError('Polling error: ' + error.message);
                        clearInterval(pollingInterval);
                    }
                }, 1000); // Poll every second
            }

            function updateWorkflowDisplay(workflow) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('workflowContainer').style.display = 'block';
                
                // Update query display
                document.getElementById('currentQuery').textContent = workflow.query;
                
                // Update progress
                document.getElementById('progressFill').style.width = workflow.progress_percentage + '%';
                document.getElementById('progressText').textContent = workflow.progress_percentage + '%';
                
                // Update steps
                const stepsContainer = document.getElementById('workflowSteps');
                stepsContainer.innerHTML = '';
                
                workflow.steps.forEach(step => {
                    const stepDiv = document.createElement('div');
                    stepDiv.className = `step ${step.status}`;
                    stepDiv.innerHTML = `
                        <h4>${step.action.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</h4>
                        <p><strong>MCP Server:</strong> ${step.mcp_server}</p>
                        <p><strong>Status:</strong> ${step.status}</p>
                        <p><strong>Details:</strong> ${step.details.description || 'No details'}</p>
                        <small>Last updated: ${new Date(step.timestamp).toLocaleTimeString()}</small>
                    `;
                    stepsContainer.appendChild(stepDiv);
                });
                
                // Show error if failed
                if (workflow.error_message) {
                    showError(workflow.error_message);
                }
            }

            function showError(message) {
                document.getElementById('loading').style.display = 'none';
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Add this endpoint to handle favicon requests
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="about:blank")


vector_service = QdrantVectorDb()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_health = await vector_service.health_check()
    return {
        "status": "healthy",
        "service": "web7-vector-search",
        "version": "1.0.0",
        "database": db_health,
    }


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


if __name__ == "__main__":
    # Run the FastAPI server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run("api:app", host=host, port=port, reload=True, log_level="info")
