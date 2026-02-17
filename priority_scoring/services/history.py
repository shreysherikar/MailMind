"""Historical response patterns service."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from models.schemas import Email, ScoreComponent
from models.database import ResponseHistoryDB


class HistoryService:
    """Service for tracking and scoring based on historical response patterns."""

    def calculate_score(
        self,
        email: Email,
        db: Optional[Session] = None
    ) -> ScoreComponent:
        """Calculate score based on historical response patterns with sender."""
        
        if not db:
            return ScoreComponent(
                score=7,
                max=15,
                reason="No history available (database not connected)",
                confidence=0.5
            )
        
        sender_email = email.sender_email.lower()
        
        # Look up history
        history = db.query(ResponseHistoryDB).filter(
            ResponseHistoryDB.sender_email == sender_email
        ).first()
        
        if not history:
            # No history - create initial record and return neutral score
            self._create_history_record(db, sender_email)
            return ScoreComponent(
                score=7,
                max=15,
                reason="New sender - no response history",
                confidence=0.5
            )
        
        # Calculate score based on response patterns
        score, reason = self._calculate_from_history(history)
        
        # Update history with new email
        self._update_history_email_received(db, history)
        
        return ScoreComponent(
            score=score,
            max=15,
            reason=reason,
            confidence=0.8
        )

    def record_response(
        self,
        db: Session,
        sender_email: str,
        response_time_hours: float
    ):
        """Record that user responded to an email from this sender."""
        
        sender_email = sender_email.lower()
        
        history = db.query(ResponseHistoryDB).filter(
            ResponseHistoryDB.sender_email == sender_email
        ).first()
        
        if not history:
            history = self._create_history_record(db, sender_email)
        
        # Update response metrics
        history.total_responses_sent += 1
        history.total_response_time_hours += response_time_hours
        history.avg_response_time_hours = (
            history.total_response_time_hours / history.total_responses_sent
        )
        history.response_rate = (
            history.total_responses_sent / max(history.total_emails_received, 1)
        )
        history.last_response_sent = datetime.now(timezone.utc)
        history.updated_at = datetime.now(timezone.utc)
        
        db.commit()

    def get_sender_history(
        self,
        db: Session,
        sender_email: str
    ) -> Optional[dict]:
        """Get response history for a sender."""
        
        history = db.query(ResponseHistoryDB).filter(
            ResponseHistoryDB.sender_email == sender_email.lower()
        ).first()
        
        if not history:
            return None
        
        return {
            "sender_email": history.sender_email,
            "total_emails_received": history.total_emails_received,
            "total_responses_sent": history.total_responses_sent,
            "avg_response_time_hours": history.avg_response_time_hours,
            "response_rate": history.response_rate,
            "last_email_received": history.last_email_received,
            "last_response_sent": history.last_response_sent,
        }

    def _create_history_record(
        self,
        db: Session,
        sender_email: str
    ) -> ResponseHistoryDB:
        """Create a new history record for a sender."""
        
        history = ResponseHistoryDB(
            id=str(uuid.uuid4()),
            sender_email=sender_email.lower(),
            total_emails_received=1,
            total_responses_sent=0,
            total_response_time_hours=0.0,
            avg_response_time_hours=0.0,
            response_rate=0.0,
            last_email_received=datetime.now(timezone.utc),
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history

    def _update_history_email_received(
        self,
        db: Session,
        history: ResponseHistoryDB
    ):
        """Update history when new email is received."""
        
        history.total_emails_received += 1
        history.last_email_received = datetime.now(timezone.utc)
        history.response_rate = (
            history.total_responses_sent / max(history.total_emails_received, 1)
        )
        history.updated_at = datetime.now(timezone.utc)
        
        db.commit()

    def _calculate_from_history(
        self,
        history: ResponseHistoryDB
    ) -> tuple:
        """Calculate priority score from response history."""
        
        score = 7  # Base score
        reasons = []
        
        # High response rate = important sender
        if history.response_rate >= 0.9:
            score += 6
            reasons.append("very high response rate (>90%)")
        elif history.response_rate >= 0.7:
            score += 4
            reasons.append("high response rate (>70%)")
        elif history.response_rate >= 0.5:
            score += 2
            reasons.append("moderate response rate")
        elif history.response_rate < 0.3 and history.total_emails_received >= 5:
            score -= 3
            reasons.append("low response rate (<30%)")
        
        # Fast response time = important sender
        if history.total_responses_sent >= 3:
            if history.avg_response_time_hours < 2:
                score += 3
                reasons.append("typically respond quickly (<2h)")
            elif history.avg_response_time_hours < 8:
                score += 1
                reasons.append("moderate response time")
            elif history.avg_response_time_hours > 48:
                score -= 2
                reasons.append("typically slow responses")
        
        # Volume bonus for frequent senders
        if history.total_emails_received >= 20:
            score += 2
            reasons.append("frequent sender")
        elif history.total_emails_received >= 10:
            score += 1
            reasons.append("regular sender")
        
        # Clamp score
        score = max(0, min(score, 15))
        
        if not reasons:
            reason = f"Based on {history.total_emails_received} previous emails"
        else:
            reason = f"History: {', '.join(reasons)}"
        
        return score, reason
