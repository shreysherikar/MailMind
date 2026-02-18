"""Pydantic schemas for request/response validation."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid


class AuthorityType(str, Enum):
    """Types of sender authority levels."""
    VIP = "vip"
    MANAGER = "manager"
    CLIENT = "client"
    RECRUITER = "recruiter"
    COLLEAGUE = "colleague"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


# ============== Email Models ==============

class Email(BaseModel):
    """Email data model."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_email: str = Field(..., description="Sender's email address")
    sender_name: Optional[str] = Field(None, description="Sender's display name")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content (plain text or HTML)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recipients: Optional[List[str]] = Field(default=[], description="List of recipient emails")
    cc: Optional[List[str]] = Field(default=[], description="CC recipients")
    has_attachments: bool = Field(default=False)

    model_config = ConfigDict(from_attributes=True)


class EmailScoreRequest(BaseModel):
    """Request model for scoring a single email."""
    email: Email


class EmailScoreBatchRequest(BaseModel):
    """Request model for scoring multiple emails."""
    emails: List[Email]


# ============== Score Models ==============

class ScoreComponent(BaseModel):
    """Individual scoring component breakdown."""
    score: int = Field(..., ge=0, description="Score achieved")
    max: int = Field(..., description="Maximum possible score")
    reason: str = Field(..., description="Explanation for the score")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of all scoring components."""
    sender_authority: ScoreComponent
    deadline_urgency: ScoreComponent
    emotional_tone: ScoreComponent
    historical_pattern: ScoreComponent
    calendar_conflict: ScoreComponent


class PriorityScore(BaseModel):
    """Complete priority score response."""
    email_id: str
    score: int = Field(..., ge=0, le=100, description="Total priority score")
    color: str = Field(..., description="Color code for visual badge")
    label: str = Field(..., description="Priority level label")
    badge: str = Field(..., description="Emoji badge")
    breakdown: ScoreBreakdown
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    scored_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class PriorityScoreBatchResponse(BaseModel):
    """Response for batch scoring."""
    scores: List[PriorityScore]
    total_emails: int
    avg_score: float


# ============== Task Models ==============

class TaskStatus(str, Enum):
    """Task status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SourceEmail(BaseModel):
    """Reference to source email for a task."""
    id: str
    subject: str
    sender: str


class Task(BaseModel):
    """Task extracted from an email."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Task title/summary")
    description: Optional[str] = Field(None, description="Detailed task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    due_date_type: Optional[str] = Field(None, description="explicit, relative, or inferred")
    priority: str = Field(default="medium", description="Priority level")
    priority_score: int = Field(default=50, ge=0, le=100)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    source_email: SourceEmail
    original_text: str = Field(..., description="Original text that triggered task extraction")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    """Model for creating a task manually."""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"
    source_email_id: Optional[str] = None


class TaskUpdate(BaseModel):
    """Model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskExtractRequest(BaseModel):
    """Request model for task extraction."""
    email: Email
    email_priority_score: Optional[int] = Field(None, description="Pre-calculated priority score")


class TaskExtractResponse(BaseModel):
    """Response model for task extraction."""
    tasks: List[Task]
    task_count: int
    source_email_id: str


class TaskCompleteResponse(BaseModel):
    """Response when completing a task."""
    task: Task
    archive_source_email: bool = Field(
        default=False,
        description="Whether to archive the source email (all tasks completed)"
    )
    source_email_id: str
    all_tasks_from_email_completed: bool


# ============== Contact Models ==============

class Contact(BaseModel):
    """Contact with authority level."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str = Field(..., description="Contact email address")
    name: Optional[str] = Field(None, description="Contact name")
    authority_type: AuthorityType = Field(default=AuthorityType.UNKNOWN)
    domain: Optional[str] = Field(None, description="Email domain")
    custom_priority_boost: int = Field(default=0, ge=-25, le=25)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class ContactCreate(BaseModel):
    """Model for creating a contact."""
    email: str
    name: Optional[str] = None
    authority_type: AuthorityType = AuthorityType.UNKNOWN
    custom_priority_boost: int = 0
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """Model for updating a contact."""
    name: Optional[str] = None
    authority_type: Optional[AuthorityType] = None
    custom_priority_boost: Optional[int] = None
    notes: Optional[str] = None


# ============== Response History ==============

class ResponseHistory(BaseModel):
    """Historical response pattern for a sender."""
    sender_email: str
    avg_response_time_hours: float
    response_rate: float = Field(..., ge=0.0, le=1.0)
    total_emails: int
    total_responses: int
    last_interaction: datetime

    model_config = ConfigDict(from_attributes=True)
