"""Tests for priority scoring functionality."""

import pytest
from datetime import datetime

from models.schemas import Email, ScoreComponent
from services.scorer import PriorityScorerService
from services.deadline import DeadlineService
from services.authority import AuthorityService
from services.tone import ToneService
from services.calendar import CalendarService
from config import get_priority_level


class TestPriorityLevels:
    """Test priority level classification."""
    
    def test_critical_level(self):
        result = get_priority_level(85)
        assert result["label"] == "critical"
        assert result["color"] == "red"
    
    def test_high_level(self):
        result = get_priority_level(70)
        assert result["label"] == "high"
        assert result["color"] == "orange"
    
    def test_medium_level(self):
        result = get_priority_level(50)
        assert result["label"] == "medium"
        assert result["color"] == "yellow"
    
    def test_low_level(self):
        result = get_priority_level(30)
        assert result["label"] == "low"
        assert result["color"] == "green"
    
    def test_minimal_level(self):
        result = get_priority_level(10)
        assert result["label"] == "minimal"
        assert result["color"] == "gray"


class TestDeadlineService:
    """Test deadline extraction and urgency scoring."""
    
    def setup_method(self):
        self.service = DeadlineService()
    
    def test_urgent_keyword_detection(self):
        email = Email(
            sender_email="test@example.com",
            subject="URGENT: Need response",
            body="This is urgent, please respond ASAP!"
        )
        result = self.service.calculate_score(email)
        assert result.score > 15
        assert "urgent" in result.reason.lower() or "asap" in result.reason.lower()
    
    def test_deadline_extraction(self):
        email = Email(
            sender_email="test@example.com",
            subject="Report due by Friday",
            body="Please submit the report by Friday."
        )
        result = self.service.calculate_score(email)
        assert result.score > 0
    
    def test_no_urgency(self):
        email = Email(
            sender_email="test@example.com",
            subject="Weekly newsletter",
            body="Here are this week's updates. No action needed."
        )
        result = self.service.calculate_score(email)
        assert result.score < 10


class TestCalendarService:
    """Test calendar conflict detection."""
    
    def setup_method(self):
        self.service = CalendarService()
    
    def test_meeting_detection(self):
        email = Email(
            sender_email="test@example.com",
            subject="Meeting tomorrow at 3pm",
            body="Let's schedule a meeting for tomorrow at 3pm."
        )
        result = self.service.calculate_score(email)
        assert result.score > 5
        assert "meeting" in result.reason.lower() or "calendar" in result.reason.lower()
    
    def test_scheduling_request(self):
        email = Email(
            sender_email="test@example.com",
            subject="Can we schedule a call?",
            body="Are you available for a call next week?"
        )
        result = self.service.calculate_score(email)
        assert result.score > 0


class TestPriorityScorerService:
    """Test the main scoring orchestrator."""
    
    def setup_method(self):
        self.service = PriorityScorerService()
    
    def test_score_email_returns_valid_score(self):
        email = Email(
            sender_email="ceo@company.com",
            sender_name="CEO",
            subject="URGENT: Review needed",
            body="Please review this immediately. Meeting tomorrow."
        )
        result = self.service.score_email(email)
        
        assert 0 <= result.score <= 100
        assert result.color in ["red", "orange", "yellow", "green", "gray"]
        assert result.label in ["critical", "high", "medium", "low", "minimal"]
        assert result.breakdown is not None
    
    def test_high_priority_email(self):
        email = Email(
            sender_email="vip@company.com",
            sender_name="John CEO",
            subject="CRITICAL: Immediate action required",
            body="This is extremely urgent! I need this done ASAP by end of day. The deadline is today!"
        )
        result = self.service.score_email(email)
        
        # Should have high urgency score
        assert result.breakdown.deadline_urgency.score > 10
    
    def test_low_priority_email(self):
        email = Email(
            sender_email="newsletter@spam.com",
            sender_name="Newsletter",
            subject="Weekly updates",
            body="Here are this week's updates. Nothing urgent."
        )
        result = self.service.score_email(email)
        
        # Should have lower score
        assert result.score < 60
    
    def test_score_breakdown_sums_correctly(self):
        email = Email(
            sender_email="test@example.com",
            subject="Test email",
            body="This is a test email."
        )
        result = self.service.score_email(email)
        
        breakdown = result.breakdown
        component_sum = (
            breakdown.sender_authority.score +
            breakdown.deadline_urgency.score +
            breakdown.emotional_tone.score +
            breakdown.historical_pattern.score +
            breakdown.calendar_conflict.score
        )
        
        assert result.score == component_sum
    
    def test_score_explanation(self):
        email = Email(
            sender_email="test@example.com",
            subject="Test",
            body="Test body"
        )
        score = self.service.score_email(email)
        explanation = self.service.get_score_explanation(score)
        
        assert "Priority Score:" in explanation
        assert "Sender Authority:" in explanation
        assert "Deadline Urgency:" in explanation


class TestEmailModel:
    """Test email model validation."""
    
    def test_email_creation(self):
        email = Email(
            sender_email="test@example.com",
            subject="Test subject",
            body="Test body"
        )
        assert email.sender_email == "test@example.com"
        assert email.subject == "Test subject"
        assert email.id is not None
    
    def test_email_with_all_fields(self):
        email = Email(
            id="custom_id",
            sender_email="sender@example.com",
            sender_name="Test Sender",
            subject="Full email",
            body="Full body content",
            timestamp=datetime.utcnow(),
            recipients=["recipient@example.com"],
            cc=["cc@example.com"],
            has_attachments=True
        )
        assert email.id == "custom_id"
        assert email.sender_name == "Test Sender"
        assert email.has_attachments is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
