"""Main priority scoring orchestrator service."""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session

from models.schemas import (
    Email, PriorityScore, ScoreBreakdown, ScoreComponent,
    PriorityScoreBatchResponse
)
from shared.database import StoredEmailDB
from shared.config import get_priority_level
from .groq_client import GroqClient, get_groq_client
from services.authority import AuthorityService
from services.deadline import DeadlineService
from services.tone import ToneService
from services.history import HistoryService
from services.calendar import CalendarService


class PriorityScorerService:
    """Main service that orchestrates all scoring components."""

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.groq = groq_client or get_groq_client()
        self.authority_service = AuthorityService(self.groq)
        self.deadline_service = DeadlineService()
        self.tone_service = ToneService(self.groq)
        self.history_service = HistoryService()
        self.calendar_service = CalendarService()

    def score_email(
        self,
        email: Email,
        db: Optional[Session] = None
    ) -> PriorityScore:
        """Calculate complete priority score for an email."""
        
        # Calculate each component
        # Calculate each component
        try:
            authority_score = self.authority_service.calculate_score(email, db)
        except Exception as e:
            print(f"Authority service failed: {e}")
            from models.schemas import ScoreComponent
            authority_score = ScoreComponent(score=50, confidence=0.0, reason="Service unavailable")

        try:
            deadline_score = self.deadline_service.calculate_score(email)
        except Exception:
             from models.schemas import ScoreComponent
             deadline_score = ScoreComponent(score=0, confidence=0.0, reason="Service unavailable")

        try:
            tone_score = self.tone_service.calculate_score(email)
        except Exception as e:
            print(f"Tone service failed: {e}")
            from models.schemas import ScoreComponent
            tone_score = ScoreComponent(score=50, confidence=0.0, reason="Service unavailable")
            
        try:
            history_score = self.history_service.calculate_score(email, db)
        except Exception:
             from models.schemas import ScoreComponent
             history_score = ScoreComponent(score=0, confidence=0.0, reason="Service unavailable")
             
        try:
            calendar_score = self.calendar_service.calculate_score(email)
        except Exception:
             from models.schemas import ScoreComponent
             calendar_score = ScoreComponent(score=0, confidence=0.0, reason="Service unavailable")
        
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
        
        # Save email to database if db session provided
        if db:
            self._save_email_to_db(db, email)
        
        return PriorityScore(
            email_id=email.id,
            score=total_score,
            color=priority_info["color"],
            label=priority_info["label"],
            badge=priority_info["badge"],
            breakdown=breakdown,
            confidence=round(overall_confidence, 2),
            scored_at=datetime.now(timezone.utc)
        )

    def _save_email_to_db(self, db: Session, email: Email):
        """Save confirmed email to storage."""
        existing = db.query(StoredEmailDB).filter(StoredEmailDB.id == email.id).first()
        if not existing:
            stored_email = StoredEmailDB(
                id=email.id,
                subject=email.subject,
                sender=email.sender_email,  # Using sender_email from schema
                recipient=email.recipients[0] if email.recipients else "",
                body=email.body,
                snippet=email.body[:150].replace("\n", " ").strip() + "...",
                received_at=email.timestamp,
                created_at=datetime.now(timezone.utc)
            )
            db.add(stored_email)
            db.commit()

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
