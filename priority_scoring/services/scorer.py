"""Main priority scoring orchestrator service."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from models.schemas import (
    Email, PriorityScore, ScoreBreakdown, ScoreComponent,
    PriorityScoreBatchResponse
)
from config import get_priority_level
from .gemini_client import GeminiClient
from .authority import AuthorityService
from .deadline import DeadlineService
from .tone import ToneService
from .history import HistoryService
from .calendar import CalendarService


class PriorityScorerService:
    """Main service that orchestrates all scoring components."""

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()
        self.authority_service = AuthorityService(self.gemini)
        self.deadline_service = DeadlineService()
        self.tone_service = ToneService(self.gemini)
        self.history_service = HistoryService()
        self.calendar_service = CalendarService()

    def score_email(
        self,
        email: Email,
        db: Optional[Session] = None
    ) -> PriorityScore:
        """Calculate complete priority score for an email."""
        
        # Calculate each component
        authority_score = self.authority_service.calculate_score(email, db)
        deadline_score = self.deadline_service.calculate_score(email)
        tone_score = self.tone_service.calculate_score(email)
        history_score = self.history_service.calculate_score(email, db)
        calendar_score = self.calendar_service.calculate_score(email)
        
        # Build breakdown
        breakdown = ScoreBreakdown(
            sender_authority=authority_score,
            deadline_urgency=deadline_score,
            emotional_tone=tone_score,
            historical_pattern=history_score,
            calendar_conflict=calendar_score
        )
        
        # Calculate total score
        total_score = (
            authority_score.score +
            deadline_score.score +
            tone_score.score +
            history_score.score +
            calendar_score.score
        )
        
        # Ensure score is in valid range
        total_score = max(0, min(total_score, 100))
        
        # Get priority level info
        priority_info = get_priority_level(total_score)
        
        # Calculate overall confidence (weighted average)
        overall_confidence = (
            authority_score.confidence * 0.25 +
            deadline_score.confidence * 0.25 +
            tone_score.confidence * 0.20 +
            history_score.confidence * 0.15 +
            calendar_score.confidence * 0.15
        )
        
        return PriorityScore(
            email_id=email.id,
            score=total_score,
            color=priority_info["color"],
            label=priority_info["label"],
            badge=priority_info["badge"],
            breakdown=breakdown,
            confidence=round(overall_confidence, 2),
            scored_at=datetime.utcnow()
        )

    def score_emails_batch(
        self,
        emails: List[Email],
        db: Optional[Session] = None
    ) -> PriorityScoreBatchResponse:
        """Score multiple emails and return batch response."""
        
        scores = []
        total_score_sum = 0
        
        for email in emails:
            score = self.score_email(email, db)
            scores.append(score)
            total_score_sum += score.score
        
        avg_score = total_score_sum / len(emails) if emails else 0
        
        return PriorityScoreBatchResponse(
            scores=scores,
            total_emails=len(emails),
            avg_score=round(avg_score, 2)
        )

    def get_score_explanation(self, priority_score: PriorityScore) -> str:
        """Generate human-readable explanation of the score."""
        
        breakdown = priority_score.breakdown
        
        explanation = f"""
Priority Score: {priority_score.score}/100 ({priority_score.label.upper()}) {priority_score.badge}

Score Breakdown:
• Sender Authority: {breakdown.sender_authority.score}/{breakdown.sender_authority.max}
  → {breakdown.sender_authority.reason}

• Deadline Urgency: {breakdown.deadline_urgency.score}/{breakdown.deadline_urgency.max}
  → {breakdown.deadline_urgency.reason}

• Emotional Tone: {breakdown.emotional_tone.score}/{breakdown.emotional_tone.max}
  → {breakdown.emotional_tone.reason}

• Historical Pattern: {breakdown.historical_pattern.score}/{breakdown.historical_pattern.max}
  → {breakdown.historical_pattern.reason}

• Calendar Conflict: {breakdown.calendar_conflict.score}/{breakdown.calendar_conflict.max}
  → {breakdown.calendar_conflict.reason}

Overall Confidence: {priority_score.confidence * 100:.0f}%
        """.strip()
        
        return explanation
