from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",  # allow your frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow_sessions = {}  # mock storage

class UserQueryRequest(BaseModel):
    query: str

@app.post("/user-query")
async def submit_query(request: UserQueryRequest, background_tasks: BackgroundTasks):
    agent_id = "mock_agent_id"
    background_tasks.add_task(lambda: None)  # mock background task
    workflow_sessions[agent_id] = {"steps": []}  # mock session
    return {
        "agent_id": agent_id,
        "status": "initiated",
        "message": "Workflow started successfully"
    }

@app.get("/workflow/{agent_id}")
async def get_workflow_status(agent_id: str):
    if agent_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent_id": agent_id, "status": "mock_status"}

@app.get("/workflow/{agent_id}/steps")
def get_steps(agent_id: str):
    if agent_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "status": 0,
        "steps": [
            {"name": "hi", "id": "0"},
            {"name": "bye", "id": "1"}
        ]
    }

@app.get("/workflow/{agent_id}/{step_id}")
def get_step_info(agent_id: str, step_id: int):
    if agent_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "step_id": step_id,
        "action": "hi",
        "mcp_server": "ya",
        "mcp_server_img_url": "https://cdn.jsdelivr.net/gh/ComposioHQ/open-logos@master/texttopdf.png",
        "status": "updated",
        "details": "here is a groq log summary"
    }

