from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Self
from enum import Enum


class UserQueryRequest(BaseModel):
    query: str


class UserQueryRequestWithId(BaseModel):
    query: str
    agent_id: str


class SearchQuery(BaseModel):
    """Model for search query request."""

    query: str = Field(
        ..., description="The search query string", min_length=1, max_length=1000
    )
    k: int = Field(
        default=1, description="The number of results to return", ge=1, le=100
    )


class TransportType(Enum):
    """The transport type."""

    STREAMABLE_HTTP = "streamable-http"
    SSE = "sse"
    STDIO = "stdio"


class MCPResponse(BaseModel):
    name: str = Field(..., description="The name of the MCP server")
    transport: TransportType = Field(..., description="The transport type")
    url: str = Field(..., description="The URL of the MCP server")
    image_url: Optional[str] = Field(
        default=None, description="The URL of the MCP server's image"
    )
    authentication: Optional[str] = Field(
        default=None, description="The authentication token"
    )


class SearchResponse(BaseModel):
    """Model for search response."""

    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The original query")
    servers: List[MCPResponse] = Field(..., description="List of search results")


class WorkflowStatus(Enum):
    STARTED = 1
    IN_PROGRESS = 2
    FAILED = 3
    SUCCEEDED = 4

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
    mcp_server_img_url: str
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
            "mcp_server_img_url": self.mcp_server_img_url,
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
        self.logs: list[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.progress_percentage = 0
        self.error_message = None

    def add_step(
        self,
        action: str,
        mcp_server: str,
        mcp_server_img_url: str,
        status: StepStatus = StepStatus.NOT_STARTED,
        details: str = None,
    ):
        step = Step(
            step_id=f"step_{len(self.steps) + 1}",
            action=action,
            mcp_server=mcp_server,
            mcp_server_img_url=mcp_server_img_url,
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
