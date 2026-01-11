"""Pydantic schemas for Priority Scoring feature."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recipients: Optional[List[str]] = Field(default=[], description="List of recipient emails")
    cc: Optional[List[str]] = Field(default=[], description="CC recipients")
    has_attachments: bool = Field(default=False)

    class Config:
        from_attributes = True


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
    scored_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class PriorityScoreBatchResponse(BaseModel):
    """Response for batch scoring."""
    scores: List[PriorityScore]
    total_emails: int
    avg_score: float


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
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
