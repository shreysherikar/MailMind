"""Reply matching service for detecting replies to tracked follow-ups."""

import re
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session

from followup_management.models.schemas import (
    FollowUp,
    FollowUpStatus,
    ReplyCheckResponse,
)
from priority_scoring.models.schemas import Email
from shared.database import FollowUpDB


class ReplyMatcherService:
    """Service for matching incoming emails to pending follow-ups."""

    def __init__(self):
        pass

    def check_if_reply(
        self,
        email: Email,
        thread_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> ReplyCheckResponse:
        """
        Check if an incoming email is a reply to a tracked follow-up.
        
        Uses multiple matching strategies:
        1. Thread ID match (most reliable)
        2. Subject line matching (Re: pattern)
        3. Sender email matching against recipients
        """
        
        if not db:
            return ReplyCheckResponse(
                is_reply=False,
                message="Database not available for reply matching"
            )
        
        # Get all pending follow-ups (waiting or overdue)
        pending_followups = db.query(FollowUpDB).filter(
            FollowUpDB.status.in_([
                FollowUpStatus.WAITING.value,
                FollowUpStatus.OVERDUE.value
            ])
        ).all()
        
        if not pending_followups:
            return ReplyCheckResponse(
                is_reply=False,
                message="No pending follow-ups to match"
            )
        
        # Try to find a match
        matched_followup = self._find_matching_followup(
            email, thread_id, pending_followups
        )
        
        if matched_followup:
            # Update the follow-up status
            matched_followup.status = FollowUpStatus.REPLIED.value
            matched_followup.replied_at = datetime.now(timezone.utc)
            matched_followup.reply_email_id = email.id
            matched_followup.reply_subject = email.subject
            matched_followup.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return ReplyCheckResponse(
                is_reply=True,
                matched_followup_id=matched_followup.id,
                matched_subject=matched_followup.subject,
                followup_status_updated=True,
                message=f"Reply matched to follow-up: {matched_followup.subject[:50]}"
            )
        
        return ReplyCheckResponse(
            is_reply=False,
            message="No matching follow-up found"
        )

    def find_potential_matches(
        self,
        email: Email,
        db: Session,
        limit: int = 5
    ) -> List[FollowUp]:
        """
        Find potential follow-up matches for an incoming email.
        Returns ranked list of possible matches without updating status.
        """
        
        pending_followups = db.query(FollowUpDB).filter(
            FollowUpDB.status.in_([
                FollowUpStatus.WAITING.value,
                FollowUpStatus.OVERDUE.value
            ])
        ).all()
        
        matches = []
        
        for followup in pending_followups:
            score = self._calculate_match_score(email, followup)
            if score > 0:
                matches.append((followup, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to FollowUp objects
        from followup_management.services.followup_detector import FollowUpDetectorService
        detector = FollowUpDetectorService()
        
        return [
            detector._db_to_followup(match[0])
            for match in matches[:limit]
        ]

    def _find_matching_followup(
        self,
        email: Email,
        thread_id: Optional[str],
        pending_followups: List[FollowUpDB]
    ) -> Optional[FollowUpDB]:
        """Find the best matching follow-up for an incoming email."""
        
        best_match = None
        best_score = 0
        
        for followup in pending_followups:
            score = 0
            
            # Strategy 1: Thread ID match (100 points - definitive)
            if thread_id and followup.thread_id and thread_id == followup.thread_id:
                return followup  # Definitive match
            
            # Strategy 2: Sender matches recipient (40 points)
            if email.sender_email and followup.recipient_email:
                if self._normalize_email(email.sender_email) == self._normalize_email(followup.recipient_email):
                    score += 40
            
            # Strategy 3: Subject line matching
            subject_score = self._match_subject(email.subject, followup.subject)
            score += subject_score
            
            # Strategy 4: Time-based scoring (replies usually come within days)
            time_score = self._time_relevance_score(email.timestamp, followup.sent_at)
            score += time_score
            
            if score > best_score:
                best_score = score
                best_match = followup
        
        # Require minimum score threshold
        if best_score >= 50:
            return best_match
        
        return None

    def _calculate_match_score(
        self,
        email: Email,
        followup: FollowUpDB
    ) -> int:
        """Calculate match score between an email and a follow-up."""
        
        score = 0
        
        # Sender matches recipient
        if email.sender_email and followup.recipient_email:
            if self._normalize_email(email.sender_email) == self._normalize_email(followup.recipient_email):
                score += 40
        
        # Subject matching
        score += self._match_subject(email.subject, followup.subject)
        
        # Time relevance
        score += self._time_relevance_score(email.timestamp, followup.sent_at)
        
        return score

    def _match_subject(self, reply_subject: str, original_subject: str) -> int:
        """
        Match subject lines and return a score.
        
        Handles common reply patterns:
        - "Re: Original Subject"
        - "RE: Original Subject"
        - "Fwd: Re: Original Subject"
        """
        
        if not reply_subject or not original_subject:
            return 0
        
        # Normalize subjects
        reply_clean = self._clean_subject(reply_subject)
        original_clean = self._clean_subject(original_subject)
        
        # Exact match after cleaning (highest score)
        if reply_clean == original_clean:
            return 50
        
        # Reply subject contains original subject
        if original_clean in reply_clean:
            return 40
        
        # Original subject contains reply subject (partial match)
        if reply_clean in original_clean:
            return 30
        
        # Check for common words (fuzzy match)
        reply_words = set(reply_clean.lower().split())
        original_words = set(original_clean.lower().split())
        
        if reply_words and original_words:
            common_words = reply_words.intersection(original_words)
            word_overlap = len(common_words) / max(len(reply_words), len(original_words))
            
            if word_overlap >= 0.5:
                return int(25 * word_overlap)
        
        return 0

    def _clean_subject(self, subject: str) -> str:
        """Remove reply/forward prefixes and clean subject line."""
        
        if not subject:
            return ""
        
        # Remove common prefixes (case-insensitive)
        patterns = [
            r'^re:\s*',
            r'^fwd:\s*',
            r'^fw:\s*',
            r'^aw:\s*',  # German reply
            r'^sv:\s*',  # Swedish reply
            r'^antw:\s*',  # German reply alternate
        ]
        
        cleaned = subject.strip()
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def _normalize_email(self, email: str) -> str:
        """Normalize email address for comparison."""
        
        if not email:
            return ""
        
        return email.lower().strip()

    def _time_relevance_score(
        self,
        reply_time: datetime,
        sent_time: datetime
    ) -> int:
        """
        Calculate time-based relevance score.
        
        Replies usually come within a reasonable timeframe.
        Score higher for more recent correspondence.
        """
        
        if not reply_time or not sent_time:
            return 0
        
        # Ensure reply_time is after sent_time
        if reply_time < sent_time:
            return 0
        
        days_diff = (reply_time - sent_time).days
        
        # Score based on how quickly the reply came
        if days_diff <= 1:
            return 15
        elif days_diff <= 3:
            return 12
        elif days_diff <= 7:
            return 8
        elif days_diff <= 14:
            return 5
        elif days_diff <= 30:
            return 2
        else:
            return 0
