from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List, Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv
from ..qdrant_vector_search.qdrant_client import QdrantVectorDb
from .models import SearchQuery, SearchResponse, UserQueryRequest
from datetime import datetime
import uuid
import asyncio
import time


load_dotenv()

app = FastAPI(
    title="Web7 Vector Search API",
    description="API for MCP server search",
    version="1.0.0"
)

workflow_sessions: Dict[str, dict] = {}

class WorkflowSession:
    def __init__(self, session_id: str, query: str):
        self.session_id = session_id
        self.query = query
        self.status = "initiated"
        self.steps = []
        self.current_step = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.progress_percentage = 0
        self.error_message = None

    def add_step(self, action: str, mcp_server: str, status: str = "started", details: dict = None):
        step = {
            "step_id": f"step_{len(self.steps) + 1}",
            "action": action,
            "mcp_server": mcp_server,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
            "duration": None
        }
        self.steps.append(step)
        self.updated_at = datetime.now()
        return step

    def update_step(self, step_id: str, status: str, details: dict = None, duration: float = None):
        for step in self.steps:
            if step["step_id"] == step_id:
                step["status"] = status
                step["timestamp"] = datetime.now().isoformat()
                if details:
                    step["details"].update(details)
                if duration:
                    step["duration"] = duration
                break
        self.updated_at = datetime.now()

    def set_progress(self, percentage: int):
        self.progress_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "query": self.query,
            "status": self.status,
            "steps": self.steps,
            "current_step": self.current_step,
            "progress_percentage": self.progress_percentage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message,
            "total_steps": len(self.steps)
        }
    
@app.post("/user-query")
async def submit_query(request: UserQueryRequest, background_tasks: BackgroundTasks):
    """Submit query and start processing in background"""
    session_id = str(uuid.uuid4())
    
    # Create workflow session
    session = WorkflowSession(session_id, request.query)
    workflow_sessions[session_id] = session
    
    # Start processing in background
    background_tasks.add_task(process_workflow, session_id)
    
    return {
        "session_id": session_id,
        "status": "initiated",
        "message": "Workflow started successfully"
    }

@app.get("/workflow/{session_id}")
async def get_workflow_status(session_id: str):
    """Get current workflow status - Frontend polls this endpoint"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = workflow_sessions[session_id]
    return session.to_dict()

@app.get("/workflow/{session_id}/graph-data")
async def get_graph_data(session_id: str):
    """Get formatted data for frontend graph visualization"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = workflow_sessions[session_id]
    
    # Format data specifically for graph visualization
    nodes = []
    edges = []
    
    for i, step in enumerate(session.steps):
        # Create node for each step
        node = {
            "id": step["step_id"],
            "label": step["action"].replace("_", " ").title(),
            "status": step["status"],
            "mcp_server": step["mcp_server"],
            "details": step["details"],
            "timestamp": step["timestamp"],
            "duration": step.get("duration"),
            "position": {"x": i * 200, "y": 100}  # Simple horizontal layout
        }
        nodes.append(node)
        
        # Create edge to next step
        if i < len(session.steps) - 1:
            edge = {
                "id": f"edge_{i}",
                "source": step["step_id"],
                "target": session.steps[i + 1]["step_id"],
                "animated": session.steps[i + 1]["status"] == "started"
            }
            edges.append(edge)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "session_info": {
            "query": session.query,
            "status": session.status,
            "progress": session.progress_percentage
        }
    }

async def process_workflow(session_id: str):
    """Main workflow processing logic - customize this for your LLM"""
    session = workflow_sessions[session_id]
    
    try:
        session.status = "processing"
        
        # Define your workflow steps
        workflow_steps = [
            {"action": "analyze_query", "mcp_server": "query_analyzer", "duration": 2},
            {"action": "select_mcp_servers", "mcp_server": "server_selector", "duration": 1},
            {"action": "connect_to_database", "mcp_server": "database_connector", "duration": 3},
            {"action": "execute_database_query", "mcp_server": "database_connector", "duration": 4},
            {"action": "process_results", "mcp_server": "data_processor", "duration": 3},
            {"action": "generate_insights", "mcp_server": "ai_analyzer", "duration": 5},
            {"action": "format_response", "mcp_server": "response_formatter", "duration": 2}
        ]
        
        total_steps = len(workflow_steps)
        
        for i, step_config in enumerate(workflow_steps):
            # Add step to session
            step = session.add_step(
                action=step_config["action"],
                mcp_server=step_config["mcp_server"],
                status="started",
                details={"description": f"Starting {step_config['action'].replace('_', ' ')}"}
            )
            
            session.current_step = i
            session.set_progress(int((i / total_steps) * 100))
            
            start_time = time.time()
            
            # Simulate the actual work (replace with your LLM/MCP calls)
            await simulate_mcp_call(step_config["action"], step_config["mcp_server"], step_config["duration"])
            
            duration = time.time() - start_time
            
            # Update step as completed
            session.update_step(
                step["step_id"],
                status="completed",
                details={
                    "description": f"Successfully completed {step_config['action'].replace('_', ' ')}",
                    "result": f"Processed by {step_config['mcp_server']}"
                },
                duration=duration
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
                current_step["step_id"],
                status="failed",
                details={"error": str(e)}
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
@app.get('/favicon.ico', include_in_schema=False)
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
        "database": db_health
    }

# GET endpoint for simple queries
@app.get("/search", response_model=SearchResponse)
async def search_vectors_get(
    query: str = Query(..., description="Search query string", min_length=1, max_length=1000),
    k: int = Query(default=1, description="Number of results", ge=1, le=100)
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
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 