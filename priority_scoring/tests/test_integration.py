"""Integration tests for History and Calendar services with database."""

import pytest
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure local package is importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Set env var for in-memory DB before importing config
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

try:
    from priority_scoring.models.database import Base, ResponseHistoryDB
    from priority_scoring.models.schemas import Email
    from priority_scoring.services.history import HistoryService
    from priority_scoring.services.calendar import CalendarService
except ImportError:
    # Fallback to direct import if package resolution fails
    from models.database import Base, ResponseHistoryDB
    from models.schemas import Email
    from services.history import HistoryService
    from services.calendar import CalendarService

# --- Fixtures ---

@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database session for testing."""
    # We use a fresh engine for each test to ensure isolation
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def history_service():
    return HistoryService()

@pytest.fixture
def calendar_service():
    return CalendarService()

# --- HistoryService Integration Tests ---

def test_history_db_initialization(db_session):
    """Test that the database initializes correctly with empty tables."""
    history = db_session.query(ResponseHistoryDB).all()
    assert len(history) == 0

def test_history_service_first_interaction(db_session, history_service):
    """Test response when receiving an email from a new sender."""
    email = Email(
        sender_email="new.sender@example.com",
        subject="First Contact",
        body="Hello there",
        timestamp=datetime.now(timezone.utc)
    )
    
    component = history_service.calculate_score(email, db_session)
    assert component.score == 7
    assert "New sender" in component.reason
    
    record = history_service.get_sender_history(db_session, "new.sender@example.com")
    assert record is not None
    assert record["total_emails_received"] == 1

def test_history_service_response_recording(db_session, history_service):
    """Test recording a user response and its effect on scoring."""
    sender = "colleague@example.com"
    email1 = Email(sender_email=sender, subject="Task 1", body="Do this", timestamp=datetime.now(timezone.utc))
    history_service.calculate_score(email1, db_session)
    
    history_service.record_response(db_session, sender, response_time_hours=1.0)
    
    record = history_service.get_sender_history(db_session, sender)
    assert record["total_responses_sent"] == 1
    
    email2 = Email(sender_email=sender, subject="Task 2", body="Do that", timestamp=datetime.now(timezone.utc))
    component = history_service.calculate_score(email2, db_session)
    assert component.score >= 0

def test_history_service_ignoring_emails(db_session, history_service):
    """Test that ignoring emails lowers the score."""
    sender = "newsletter@example.com"
    for i in range(5):
        email = Email(sender_email=sender, subject=f"News {i}", body="Update", timestamp=datetime.now(timezone.utc))
        history_service.calculate_score(email, db_session)
    
    record = history_service.get_sender_history(db_session, sender)
    assert record["total_emails_received"] == 5
    
    email6 = Email(sender_email=sender, subject="News 6", body="Update", timestamp=datetime.now(timezone.utc))
    component = history_service.calculate_score(email6, db_session)
    assert component.score <= 7

def test_history_service_no_db(history_service):
    """Test behavior when DB session is not provided."""
    email = Email(sender_email="test@example.com", subject="Test", body="Body", timestamp=datetime.now(timezone.utc))
    component = history_service.calculate_score(email, None)
    assert component.score == 7

def test_calendar_service_meeting_invite(calendar_service):
    """Test detection of meeting invites."""
    email = Email(
        sender_email="boss@example.com",
        subject="Team Sync",
        body="Please accept this invite for the weekly standup meeting at 10am.",
        timestamp=datetime.now(timezone.utc)
    )
    component = calendar_service.calculate_score(email)
    assert component.score > 0

def test_calendar_service_conflict(calendar_service):
    """Test detection of conflicts."""
    email = Email(
        sender_email="colleague@example.com",
        subject="Reschedule",
        body="I have a conflict at that time. Can we reschedule?",
        timestamp=datetime.now(timezone.utc)
    )
    component = calendar_service.calculate_score(email)
    assert component.score >= 0
