"""Pydantic schemas for Follow-up Management feature."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

# Import Email from priority_scoring for consistency
from priority_scoring.models.schemas import Email


class FollowUpStatus(str, Enum):
    """Follow-up status options."""
    WAITING = "waiting"
    REPLIED = "replied"
    NO_REPLY_NEEDED = "no_reply_needed"
    OVERDUE = "overdue"
    ARCHIVED = "archived"


class FollowUpIntent(BaseModel):
    """AI-detected intent for follow-up."""
    expects_reply: bool = Field(..., description="Whether the email expects a reply")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    reasons: List[str] = Field(default=[], description="Reasons for the detection")
    suggested_followup_days: int = Field(default=3, description="Suggested days before marking overdue")
    question_count: int = Field(default=0, description="Number of questions asked")
    request_count: int = Field(default=0, description="Number of requests made")
    action_items_assigned: int = Field(default=0, description="Action items assigned to recipient")


class FollowUp(BaseModel):
    """Follow-up tracking model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Source email info
    email_id: str = Field(..., description="ID of the sent email being tracked")
    subject: str = Field(..., description="Email subject line")
    recipient_email: str = Field(..., description="Primary recipient email")
    recipient_name: Optional[str] = Field(None, description="Recipient display name")
    snippet: Optional[str] = Field(None, description="Email preview snippet")
    
    # Timestamps
    sent_at: datetime = Field(..., description="When the email was sent")
    expected_reply_by: Optional[datetime] = Field(None, description="Expected reply deadline")
    replied_at: Optional[datetime] = Field(None, description="When reply was received")
    
    # Status tracking
    status: FollowUpStatus = Field(default=FollowUpStatus.WAITING)
    days_waiting: int = Field(default=0, description="Days since sent without reply")
    
    # AI detection results
    expects_reply: bool = Field(default=True)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    detection_reasons: List[str] = Field(default=[], description="Why follow-up was detected")
    
    # Reply info
    reply_email_id: Optional[str] = Field(None, description="ID of the reply email")
    reply_subject: Optional[str] = Field(None, description="Subject of reply")
    
    # Metadata
    thread_id: Optional[str] = Field(None, description="Email thread ID for matching")
    reminder_sent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class FollowUpCreate(BaseModel):
    """Model for manually creating a follow-up."""
    email_id: str
    subject: str
    recipient_email: str
    recipient_name: Optional[str] = None
    snippet: Optional[str] = None
    sent_at: datetime
    expected_reply_by: Optional[datetime] = None
    thread_id: Optional[str] = None


class FollowUpUpdate(BaseModel):
    """Model for updating a follow-up."""
    status: Optional[FollowUpStatus] = None
    expected_reply_by: Optional[datetime] = None
    reply_email_id: Optional[str] = None
    reply_subject: Optional[str] = None
    replied_at: Optional[datetime] = None


class FollowUpDetectRequest(BaseModel):
    """Request model for detecting follow-up potential in a sent email."""
    email: Email
    thread_id: Optional[str] = Field(None, description="Thread ID for reply matching")


class FollowUpDetectResponse(BaseModel):
    """Response model for follow-up detection."""
    followup: Optional[FollowUp] = Field(None, description="Created follow-up if detected")
    intent: FollowUpIntent
    should_track: bool = Field(..., description="Whether this email should be tracked")
    message: str = Field(..., description="Human-readable explanation")


class FollowUpBatchDetectRequest(BaseModel):
    """Request for batch follow-up detection."""
    emails: List[Email]


class FollowUpBatchDetectResponse(BaseModel):
    """Response for batch follow-up detection."""
    results: List[FollowUpDetectResponse]
    total_emails: int
    tracked_count: int


class ReplyCheckRequest(BaseModel):
    """Request to check if an incoming email is a reply."""
    email: Email
    thread_id: Optional[str] = Field(None, description="Thread ID from email client")


class ReplyCheckResponse(BaseModel):
    """Response for reply check."""
    is_reply: bool = Field(..., description="Whether this is a reply to a tracked email")
    matched_followup_id: Optional[str] = Field(None, description="ID of matched follow-up")
    matched_subject: Optional[str] = Field(None, description="Subject of original email")
    followup_status_updated: bool = Field(default=False)
    message: str


class FollowUpStats(BaseModel):
    """Statistics about follow-ups."""
    total: int = 0
    waiting: int = 0
    overdue: int = 0
    replied: int = 0
    avg_response_time_hours: Optional[float] = None
