"""Pydantic schemas for Smart Task Extraction feature."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

from priority_scoring.models.schemas import Email


class TaskStatus(str, Enum):
    """Task status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SourceEmail(BaseModel):
    """Reference to the source email for a task."""
    id: str
    subject: str
    sender: str


class Task(BaseModel):
    """Extracted task model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Brief task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    due_date_type: Optional[str] = Field(None, description="'explicit' or 'relative'")
    priority: str = Field(default="medium", description="Inherited from email priority")
    priority_score: int = Field(default=50, ge=0, le=100)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    source_email: Optional[SourceEmail] = Field(None, description="Reference to source email")
    original_text: str = Field(..., description="Original text containing the task")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    """Model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskExtractRequest(BaseModel):
    """Request model for extracting tasks from an email."""
    email: Email
    email_priority_score: Optional[int] = Field(None, description="Pre-calculated email priority score")


class TaskExtractResponse(BaseModel):
    """Response model for task extraction."""
    tasks: List[Task]
    task_count: int
    source_email_id: str


class TaskCompleteResponse(BaseModel):
    """Response when completing a task."""
    task: Task
    archive_source_email: bool = Field(default=False, description="True if all tasks from source email are completed")
    source_email_id: str
    all_tasks_from_email_completed: bool
