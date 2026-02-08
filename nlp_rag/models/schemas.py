"""Data schemas for NLP & RAG features."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class IntentType(str, Enum):
    """Email intent types."""
    REQUEST = "request"
    QUESTION = "question"
    INFORMATION = "information"
    COMPLAINT = "complaint"
    MEETING = "meeting"
    FOLLOWUP = "followup"
    ACKNOWLEDGMENT = "acknowledgment"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Named entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    DATE = "date"
    LOCATION = "location"
    MONEY = "money"
    PROJECT = "project"
    PRODUCT = "product"


class Entity(BaseModel):
    """Named entity extracted from text."""
    text: str
    type: EntityType
    confidence: float = Field(ge=0.0, le=1.0)
    context: Optional[str] = None


class EmailSummary(BaseModel):
    """Email summary response."""
    email_id: str
    short_summary: str = Field(description="One-line summary (max 100 chars)")
    detailed_summary: str = Field(description="Detailed summary (2-3 sentences)")
    key_points: List[str] = Field(description="Bullet points of key information")
    action_items: List[str] = Field(description="Extracted action items")
    entities: List[Entity] = Field(description="Named entities found")
    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)


class SearchQuery(BaseModel):
    """Semantic search query."""
    query: str = Field(description="Natural language search query")
    limit: int = Field(default=10, ge=1, le=50)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sender_filter: Optional[str] = None


class SearchResult(BaseModel):
    """Single search result."""
    email_id: str
    subject: str
    sender: str
    date: datetime
    snippet: str = Field(description="Relevant excerpt from email")
    similarity_score: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results response."""
    query: str
    results: List[SearchResult]
    total_found: int
    search_time_ms: float


class CompanyMemoryEntry(BaseModel):
    """Entry in company knowledge base."""
    id: str
    content: str
    source_email_id: Optional[str] = None
    category: str = Field(description="e.g., 'policy', 'project', 'decision'")
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class CompanyMemoryQuery(BaseModel):
    """Query for company memory."""
    question: str = Field(description="Natural language question")
    limit: int = Field(default=5, ge=1, le=20)


class CompanyMemoryResponse(BaseModel):
    """Response from company memory."""
    question: str
    answer: str = Field(description="AI-generated answer")
    sources: List[SearchResult] = Field(description="Source emails used")
    confidence: float = Field(ge=0.0, le=1.0)


class BurnoutSignal(str, Enum):
    """Types of burnout signals."""
    LATE_NIGHT_EMAILS = "late_night_emails"
    WEEKEND_WORK = "weekend_work"
    HIGH_VOLUME = "high_volume"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    STRESS_LANGUAGE = "stress_language"
    RESPONSE_DELAY = "response_delay"


class BurnoutMetrics(BaseModel):
    """Burnout detection metrics."""
    user_email: str
    period_start: datetime
    period_end: datetime
    
    # Email patterns
    total_emails_sent: int
    total_emails_received: int
    late_night_count: int = Field(description="Emails sent after 10 PM")
    weekend_count: int = Field(description="Emails sent on weekends")
    avg_response_time_hours: float
    
    # Sentiment metrics
    avg_sentiment_score: float = Field(ge=-1.0, le=1.0)
    stress_level: float = Field(ge=0.0, le=100.0)
    negative_email_ratio: float = Field(ge=0.0, le=1.0)
    
    # Workload
    daily_email_avg: float
    peak_day_count: int
    
    # Signals detected
    signals: List[BurnoutSignal]
    risk_score: float = Field(ge=0.0, le=100.0, description="Overall burnout risk")
    risk_level: str = Field(description="low, moderate, high, critical")
    
    recommendations: List[str] = Field(description="Actionable suggestions")


class NLPAnalysis(BaseModel):
    """Complete NLP analysis of an email."""
    email_id: str
    summary: EmailSummary
    sentiment: Dict[str, float] = Field(description="Sentiment scores")
    intent: IntentType
    entities: List[Entity]
    language: str = Field(default="en")
    readability_score: Optional[float] = Field(ge=0.0, le=100.0)
    word_count: int
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
