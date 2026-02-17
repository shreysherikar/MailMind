"""SQLAlchemy database models and connection setup."""

from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

from shared.config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ContactDB(Base):
    """Database model for contacts with authority levels."""
    __tablename__ = "contacts"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    authority_type = Column(String, default="unknown")
    domain = Column(String, nullable=True, index=True)
    custom_priority_boost = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ResponseHistoryDB(Base):
    """Database model for tracking response patterns per sender."""
    __tablename__ = "response_history"

    id = Column(String, primary_key=True, index=True)
    sender_email = Column(String, index=True, nullable=False)
    total_emails_received = Column(Integer, default=0)
    total_responses_sent = Column(Integer, default=0)
    total_response_time_hours = Column(Float, default=0.0)
    avg_response_time_hours = Column(Float, default=0.0)
    response_rate = Column(Float, default=0.0)
    last_email_received = Column(DateTime, nullable=True)
    last_response_sent = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class TaskDB(Base):
    """Database model for extracted tasks."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    due_date_type = Column(String, nullable=True)
    priority = Column(String, default="medium")
    priority_score = Column(Integer, default=50)
    status = Column(String, default="pending", index=True)
    
    # Source email reference
    source_email_id = Column(String, index=True, nullable=False)
    source_email_subject = Column(String, nullable=True)
    source_email_sender = Column(String, nullable=True)
    
    original_text = Column(Text, nullable=False)
    confidence = Column(Float, default=0.8)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class EmailScoreCache(Base):
    """Cache for email scores to avoid re-scoring."""
    __tablename__ = "email_score_cache"

    email_id = Column(String, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    color = Column(String, nullable=False)
    label = Column(String, nullable=False)
    breakdown_json = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    scored_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FollowUpDB(Base):
    """Database model for follow-up tracking."""
    __tablename__ = "followups"

    id = Column(String, primary_key=True, index=True)
    
    # Source email info
    email_id = Column(String, index=True, nullable=False)
    subject = Column(String, nullable=False)
    recipient_email = Column(String, index=True, nullable=False)
    recipient_name = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, nullable=False)
    expected_reply_by = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(String, default="waiting", index=True)
    days_waiting = Column(Integer, default=0)
    
    # AI detection results
    expects_reply = Column(Boolean, default=True)
    confidence = Column(Float, default=0.7)
    detection_reasons = Column(Text, nullable=True)  # JSON array
    
    # Reply info
    reply_email_id = Column(String, nullable=True)
    reply_subject = Column(String, nullable=True)
    
    # Metadata
    thread_id = Column(String, nullable=True, index=True)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class StoredEmailDB(Base):
    """Database model for storing full email content."""
    __tablename__ = "stored_emails"

    id = Column(String, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    snippet = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False)
    
    # Metadata
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Link to caching
    score_cache_id = Column(String, nullable=True)
    
    # Status tracking (Final features)
    status = Column(String, default="inbox", index=True) # inbox, done, archived, snoozed
    snoozed_until = Column(DateTime, nullable=True)
    

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)
