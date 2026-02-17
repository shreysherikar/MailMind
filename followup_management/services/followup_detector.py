"""Follow-up detection service for analyzing sent emails."""

from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import json

from sqlalchemy.orm import Session

from followup_management.models.schemas import (
    FollowUp,
    FollowUpStatus,
    FollowUpIntent,
    FollowUpDetectResponse,
    FollowUpBatchDetectResponse,
    FollowUpStats,
)
from priority_scoring.models.schemas import Email
from shared.database import FollowUpDB
from shared.groq_client import GroqClient, get_groq_client


class FollowUpDetectorService:
    """Service for detecting and tracking follow-ups from sent emails."""

    # Default days before marking as overdue
    DEFAULT_OVERDUE_DAYS = 3

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.groq = groq_client or get_groq_client()

    def detect_followup(
        self,
        email: Email,
        thread_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> FollowUpDetectResponse:
        """Analyze a sent email to detect if it expects a reply."""
        
        # Get AI-powered intent detection
        intent = self._analyze_followup_intent(email)
        
        # Determine if we should track this email
        should_track = intent.expects_reply and intent.confidence >= 0.5
        
        followup = None
        message = ""
        
        if should_track:
            # Create follow-up tracking entry
            followup = self._create_followup(email, intent, thread_id)
            
            # Save to database if available
            if db:
                self._save_followup_to_db(db, followup)
            
            message = f"Tracking follow-up: {len(intent.reasons)} signals detected"
        else:
            if not intent.expects_reply:
                message = "Email does not appear to expect a reply"
            else:
                message = f"Low confidence ({intent.confidence:.0%}) - not tracking"
        
        return FollowUpDetectResponse(
            followup=followup,
            intent=intent,
            should_track=should_track,
            message=message
        )

    def detect_followups_batch(
        self,
        emails: List[Email],
        db: Optional[Session] = None
    ) -> FollowUpBatchDetectResponse:
        """Detect follow-ups for multiple emails."""
        
        results = []
        tracked_count = 0
        
        for email in emails:
            result = self.detect_followup(email, db=db)
            results.append(result)
            if result.should_track:
                tracked_count += 1
        
        return FollowUpBatchDetectResponse(
            results=results,
            total_emails=len(emails),
            tracked_count=tracked_count
        )

    def get_followups(
        self,
        db: Session,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[FollowUp]:
        """Get follow-ups from database with optional status filter."""
        
        query = db.query(FollowUpDB)
        
        if status:
            query = query.filter(FollowUpDB.status == status)
        
        # Update days_waiting and overdue status for waiting items
        self._update_waiting_status(db)
        
        query = query.order_by(FollowUpDB.sent_at.desc())
        query = query.limit(limit)
        
        db_followups = query.all()
        
        return [self._db_to_followup(f) for f in db_followups]

    def get_waiting_followups(self, db: Session, limit: int = 100) -> List[FollowUp]:
        """Get all follow-ups still waiting for reply."""
        
        self._update_waiting_status(db)
        
        db_followups = db.query(FollowUpDB).filter(
            FollowUpDB.status.in_([FollowUpStatus.WAITING.value, FollowUpStatus.OVERDUE.value])
        ).order_by(FollowUpDB.sent_at.asc()).limit(limit).all()
        
        return [self._db_to_followup(f) for f in db_followups]

    def get_overdue_followups(self, db: Session, limit: int = 100) -> List[FollowUp]:
        """Get follow-ups that are overdue."""
        
        self._update_waiting_status(db)
        
        db_followups = db.query(FollowUpDB).filter(
            FollowUpDB.status == FollowUpStatus.OVERDUE.value
        ).order_by(FollowUpDB.days_waiting.desc()).limit(limit).all()
        
        return [self._db_to_followup(f) for f in db_followups]

    def get_followup_by_id(self, db: Session, followup_id: str) -> Optional[FollowUp]:
        """Get a single follow-up by ID."""
        
        db_followup = db.query(FollowUpDB).filter(FollowUpDB.id == followup_id).first()
        
        if not db_followup:
            return None
        
        return self._db_to_followup(db_followup)

    def update_followup(
        self,
        db: Session,
        followup_id: str,
        updates: dict
    ) -> Optional[FollowUp]:
        """Update a follow-up."""
        
        db_followup = db.query(FollowUpDB).filter(FollowUpDB.id == followup_id).first()
        
        if not db_followup:
            return None
        
        for key, value in updates.items():
            if hasattr(db_followup, key) and value is not None:
                if key == "status" and hasattr(value, "value"):
                    setattr(db_followup, key, value.value)
                else:
                    setattr(db_followup, key, value)
        
        db_followup.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_followup)
        
        return self._db_to_followup(db_followup)

    def mark_as_replied(
        self,
        db: Session,
        followup_id: str,
        reply_email_id: str,
        reply_subject: Optional[str] = None
    ) -> Optional[FollowUp]:
        """Mark a follow-up as replied."""
        
        return self.update_followup(db, followup_id, {
            "status": FollowUpStatus.REPLIED,
            "replied_at": datetime.utcnow(),
            "reply_email_id": reply_email_id,
            "reply_subject": reply_subject
        })

    def delete_followup(self, db: Session, followup_id: str) -> bool:
        """Delete a follow-up."""
        
        db_followup = db.query(FollowUpDB).filter(FollowUpDB.id == followup_id).first()
        
        if not db_followup:
            return False
        
        db.delete(db_followup)
        db.commit()
        
        return True

    def get_stats(self, db: Session) -> FollowUpStats:
        """Get follow-up statistics."""
        
        self._update_waiting_status(db)
        
        total = db.query(FollowUpDB).count()
        waiting = db.query(FollowUpDB).filter(FollowUpDB.status == FollowUpStatus.WAITING.value).count()
        overdue = db.query(FollowUpDB).filter(FollowUpDB.status == FollowUpStatus.OVERDUE.value).count()
        replied = db.query(FollowUpDB).filter(FollowUpDB.status == FollowUpStatus.REPLIED.value).count()
        
        # Calculate average response time for replied items
        avg_response_time = None
        replied_items = db.query(FollowUpDB).filter(
            FollowUpDB.status == FollowUpStatus.REPLIED.value,
            FollowUpDB.replied_at.isnot(None)
        ).all()
        
        if replied_items:
            total_hours = sum(
                (item.replied_at - item.sent_at).total_seconds() / 3600
                for item in replied_items
                if item.replied_at
            )
            avg_response_time = total_hours / len(replied_items)
        
        return FollowUpStats(
            total=total,
            waiting=waiting,
            overdue=overdue,
            replied=replied,
            avg_response_time_hours=round(avg_response_time, 2) if avg_response_time else None
        )

    def _analyze_followup_intent(self, email: Email) -> FollowUpIntent:
        """Use AI to analyze if email expects a reply."""
        
        if self.groq.is_available:
            return self._ai_analyze_intent(email)
        else:
            return self._fallback_analyze_intent(email)

    def _ai_analyze_intent(self, email: Email) -> FollowUpIntent:
        """AI-powered intent analysis using Groq."""
        
        prompt = f"""Analyze this sent email and determine if it expects a reply from the recipient.

Return a JSON object with:
- expects_reply: boolean - Does this email expect/need a reply?
- confidence: 0.0-1.0 - How confident are you?
- reasons: array of strings - Why does it expect a reply (or not)?
- suggested_followup_days: integer (1-14) - How many days before considering overdue?
- question_count: integer - How many direct questions are asked?
- request_count: integer - How many requests/asks are made?
- action_items_assigned: integer - How many action items assigned to recipient?

Subject: {email.subject}

Body:
\"\"\"
{email.body[:2000]}
\"\"\"

Return ONLY valid JSON, no other text."""

        try:
            response = self.groq.generate_text(prompt, max_tokens=500)
            if response:
                result = self.groq._parse_json_response(response)
            
            if result:
                return FollowUpIntent(
                    expects_reply=result.get("expects_reply", False),
                    confidence=result.get("confidence", 0.5),
                    reasons=result.get("reasons", []),
                    suggested_followup_days=result.get("suggested_followup_days", 3),
                    question_count=result.get("question_count", 0),
                    request_count=result.get("request_count", 0),
                    action_items_assigned=result.get("action_items_assigned", 0)
                )
        except Exception as e:
            print(f"Groq follow-up analysis error: {e}")
        
        return self._fallback_analyze_intent(email)

    def _fallback_analyze_intent(self, email: Email) -> FollowUpIntent:
        """Rule-based fallback for intent analysis."""
        
        text = f"{email.subject} {email.body}".lower()
        
        expects_reply = False
        confidence = 0.5
        reasons = []
        question_count = 0
        request_count = 0
        action_items = 0
        suggested_days = 3
        
        # Count question marks (direct questions)
        question_count = text.count("?")
        if question_count > 0:
            expects_reply = True
            reasons.append(f"{question_count} question(s) asked")
            confidence += 0.15 * min(question_count, 3)
        
        # Check for request patterns
        request_patterns = [
            "please let me know",
            "please respond",
            "please reply",
            "please confirm",
            "please advise",
            "get back to me",
            "let me know",
            "waiting for your",
            "waiting to hear",
            "looking forward to your reply",
            "looking forward to hearing",
            "could you please",
            "can you please",
            "would you please",
            "i need you to",
            "please send",
            "please provide",
            "please share",
        ]
        
        for pattern in request_patterns:
            if pattern in text:
                request_count += 1
                expects_reply = True
                reasons.append(f"Request pattern: '{pattern}'")
                confidence += 0.1
        
        # Check for action assignments
        action_patterns = [
            "action required",
            "your action",
            "please review",
            "please complete",
            "please update",
            "please submit",
            "your feedback",
            "your input",
            "your thoughts",
        ]
        
        for pattern in action_patterns:
            if pattern in text:
                action_items += 1
                expects_reply = True
                reasons.append(f"Action assigned: '{pattern}'")
                confidence += 0.1
        
        # Check for urgency (affects suggested days)
        urgent_patterns = ["urgent", "asap", "immediately", "today", "by tomorrow"]
        for pattern in urgent_patterns:
            if pattern in text:
                suggested_days = 1
                reasons.append(f"Urgent indicator: '{pattern}'")
                break
        
        # Reduce confidence for newsletters/automated patterns
        auto_patterns = ["unsubscribe", "no-reply", "noreply", "do not reply", "automated"]
        for pattern in auto_patterns:
            if pattern in text:
                expects_reply = False
                confidence = 0.9  # High confidence it doesn't need reply
                reasons = ["Appears to be automated/no-reply email"]
                break
        
        # Cap confidence
        confidence = min(confidence, 0.95)
        
        return FollowUpIntent(
            expects_reply=expects_reply,
            confidence=round(confidence, 2),
            reasons=reasons[:5],  # Limit to 5 reasons
            suggested_followup_days=suggested_days,
            question_count=question_count,
            request_count=min(request_count, 10),
            action_items_assigned=min(action_items, 5)
        )

    def _create_followup(
        self,
        email: Email,
        intent: FollowUpIntent,
        thread_id: Optional[str] = None
    ) -> FollowUp:
        """Create a FollowUp object from email and intent."""
        
        # Extract recipient (first one if multiple)
        recipient_email = email.recipients[0] if email.recipients else "unknown@email.com"
        
        # Create snippet from body
        snippet = email.body[:150].replace("\n", " ").strip()
        if len(email.body) > 150:
            snippet += "..."
        
        # Calculate expected reply date
        expected_reply_by = datetime.utcnow() + timedelta(days=intent.suggested_followup_days)
        
        return FollowUp(
            id=str(uuid.uuid4()),
            email_id=email.id,
            subject=email.subject,
            recipient_email=recipient_email,
            recipient_name=None,
            snippet=snippet,
            sent_at=email.timestamp,
            expected_reply_by=expected_reply_by,
            status=FollowUpStatus.WAITING,
            days_waiting=0,
            expects_reply=intent.expects_reply,
            confidence=intent.confidence,
            detection_reasons=intent.reasons,
            thread_id=thread_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def _update_waiting_status(self, db: Session):
        """Update days_waiting and status for all waiting follow-ups."""
        
        waiting_followups = db.query(FollowUpDB).filter(
            FollowUpDB.status == FollowUpStatus.WAITING.value
        ).all()
        
        now = datetime.utcnow()
        
        for followup in waiting_followups:
            days_waiting = (now - followup.sent_at).days
            followup.days_waiting = days_waiting
            
            # Check if overdue (past expected_reply_by or > DEFAULT_OVERDUE_DAYS)
            if followup.expected_reply_by and now > followup.expected_reply_by:
                followup.status = FollowUpStatus.OVERDUE.value
            elif days_waiting > self.DEFAULT_OVERDUE_DAYS:
                followup.status = FollowUpStatus.OVERDUE.value
            
            followup.updated_at = now
        
        db.commit()

    def _save_followup_to_db(self, db: Session, followup: FollowUp):
        """Save a follow-up to the database."""
        
        db_followup = FollowUpDB(
            id=followup.id,
            email_id=followup.email_id,
            subject=followup.subject,
            recipient_email=followup.recipient_email,
            recipient_name=followup.recipient_name,
            snippet=followup.snippet,
            sent_at=followup.sent_at,
            expected_reply_by=followup.expected_reply_by,
            status=followup.status.value,
            days_waiting=followup.days_waiting,
            expects_reply=followup.expects_reply,
            confidence=followup.confidence,
            detection_reasons=json.dumps(followup.detection_reasons),
            thread_id=followup.thread_id,
            created_at=followup.created_at,
            updated_at=followup.updated_at
        )
        
        db.add(db_followup)
        db.commit()

    def _db_to_followup(self, db_followup: FollowUpDB) -> FollowUp:
        """Convert database model to FollowUp schema."""
        
        # Parse detection_reasons from JSON string
        detection_reasons = []
        if db_followup.detection_reasons:
            try:
                detection_reasons = json.loads(db_followup.detection_reasons)
            except (json.JSONDecodeError, TypeError):
                detection_reasons = []
        
        return FollowUp(
            id=db_followup.id,
            email_id=db_followup.email_id,
            subject=db_followup.subject,
            recipient_email=db_followup.recipient_email,
            recipient_name=db_followup.recipient_name,
            snippet=db_followup.snippet,
            sent_at=db_followup.sent_at,
            expected_reply_by=db_followup.expected_reply_by,
            replied_at=db_followup.replied_at,
            status=FollowUpStatus(db_followup.status),
            days_waiting=db_followup.days_waiting,
            expects_reply=db_followup.expects_reply,
            confidence=db_followup.confidence,
            detection_reasons=detection_reasons,
            reply_email_id=db_followup.reply_email_id,
            reply_subject=db_followup.reply_subject,
            thread_id=db_followup.thread_id,
            reminder_sent=db_followup.reminder_sent,
            created_at=db_followup.created_at,
            updated_at=db_followup.updated_at
        )
