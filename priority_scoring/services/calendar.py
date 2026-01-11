"""Calendar conflict detection service."""

import re
from typing import List, Tuple

from priority_scoring.models.schemas import Email, ScoreComponent


class CalendarService:
    """Service for detecting calendar-related mentions and conflicts."""

    # Meeting-related keywords
    MEETING_KEYWORDS = [
        "meeting", "call", "sync", "standup", "stand-up", "huddle",
        "conference", "discussion", "catch up", "catch-up", "touchbase",
        "one-on-one", "1:1", "review meeting", "demo", "presentation",
        "interview", "workshop", "training", "webinar", "town hall"
    ]

    # Scheduling keywords that suggest action needed
    SCHEDULING_KEYWORDS = [
        "schedule", "reschedule", "book", "calendar", "availability",
        "free time", "slot", "when are you", "can we meet", "let's meet",
        "set up a", "arrange", "plan for", "block time", "hold time"
    ]

    # Time-specific patterns
    TIME_PATTERNS = [
        r"\d{1,2}:\d{2}\s*(?:am|pm)?",
        r"\d{1,2}\s*(?:am|pm)",
        r"(?:at|by|around)\s+\d{1,2}",
        r"(?:morning|afternoon|evening|noon|midnight)",
    ]

    # Conflict indicators
    CONFLICT_KEYWORDS = [
        "conflict", "double-booked", "overlap", "clash", "same time",
        "already scheduled", "can't make it", "won't be able", "reschedule"
    ]

    def calculate_score(self, email: Email) -> ScoreComponent:
        """Calculate calendar conflict score from email."""
        
        text = f"{email.subject} {email.body}".lower()
        
        score = 0
        reasons = []
        
        # Check for meeting mentions
        meeting_score, meeting_reasons = self._check_meeting_mentions(text)
        score += meeting_score
        reasons.extend(meeting_reasons)
        
        # Check for scheduling requests
        scheduling_score, scheduling_reasons = self._check_scheduling_requests(text)
        score += scheduling_score
        reasons.extend(scheduling_reasons)
        
        # Check for time-specific mentions
        time_score, time_reasons = self._check_time_mentions(text)
        score += time_score
        reasons.extend(time_reasons)
        
        # Check for conflict indicators
        conflict_score, conflict_reasons = self._check_conflicts(text)
        score += conflict_score
        reasons.extend(conflict_reasons)
        
        # Cap the score
        final_score = min(score, 15)
        
        if not reasons:
            reason = "No calendar-related content detected"
            confidence = 0.7
        else:
            reason = f"Calendar: {', '.join(reasons[:3])}"
            confidence = 0.8
        
        return ScoreComponent(
            score=final_score,
            max=15,
            reason=reason,
            confidence=confidence
        )

    def _check_meeting_mentions(self, text: str) -> Tuple[int, List[str]]:
        """Check for meeting-related keywords."""
        
        score = 0
        reasons = []
        
        for keyword in self.MEETING_KEYWORDS:
            if keyword in text:
                score += 4
                reasons.append(f"meeting mention ('{keyword}')")
                break  # Only count once
        
        # Check for meeting invites
        if "invite" in text and any(kw in text for kw in self.MEETING_KEYWORDS):
            score += 3
            reasons.append("meeting invite")
        
        # Check for recurring meeting patterns
        if any(word in text for word in ["weekly", "daily", "monthly", "recurring"]):
            score += 2
            reasons.append("recurring meeting")
        
        return min(score, 8), reasons

    def _check_scheduling_requests(self, text: str) -> Tuple[int, List[str]]:
        """Check for scheduling-related requests."""
        
        score = 0
        reasons = []
        
        for keyword in self.SCHEDULING_KEYWORDS:
            if keyword in text:
                score += 5
                reasons.append("scheduling request")
                break
        
        # Check for availability questions
        availability_patterns = [
            "are you available",
            "are you free",
            "what time works",
            "when can you",
            "your availability",
            "open slots",
        ]
        
        for pattern in availability_patterns:
            if pattern in text:
                score += 4
                reasons.append("availability inquiry")
                break
        
        return min(score, 8), reasons

    def _check_time_mentions(self, text: str) -> Tuple[int, List[str]]:
        """Check for specific time mentions."""
        
        score = 0
        reasons = []
        
        # Check for time patterns
        for pattern in self.TIME_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 3
                reasons.append("specific time mentioned")
                break
        
        # Check for day mentions
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in text:
                score += 2
                reasons.append(f"day mentioned ({day})")
                break
        
        # Check for "today" or "tomorrow"
        if "today" in text or "tomorrow" in text:
            score += 4
            reasons.append("imminent time reference")
        
        return min(score, 6), reasons

    def _check_conflicts(self, text: str) -> Tuple[int, List[str]]:
        """Check for conflict indicators."""
        
        score = 0
        reasons = []
        
        for keyword in self.CONFLICT_KEYWORDS:
            if keyword in text:
                score += 6
                reasons.append("potential conflict")
                break
        
        # Check for cancellation
        cancel_words = ["cancel", "postpone", "move", "push back", "delay"]
        for word in cancel_words:
            if word in text:
                score += 4
                reasons.append("schedule change request")
                break
        
        return min(score, 8), reasons

    def extract_meeting_details(self, text: str) -> dict:
        """Extract meeting details from email text (for debugging/display)."""
        
        text_lower = text.lower()
        
        details = {
            "has_meeting_mention": False,
            "meeting_types": [],
            "has_time": False,
            "has_scheduling_request": False,
            "has_conflict": False,
        }
        
        # Check meeting types
        for keyword in self.MEETING_KEYWORDS:
            if keyword in text_lower:
                details["has_meeting_mention"] = True
                details["meeting_types"].append(keyword)
        
        # Check for time
        for pattern in self.TIME_PATTERNS:
            if re.search(pattern, text_lower):
                details["has_time"] = True
                break
        
        # Check scheduling
        for keyword in self.SCHEDULING_KEYWORDS:
            if keyword in text_lower:
                details["has_scheduling_request"] = True
                break
        
        # Check conflicts
        for keyword in self.CONFLICT_KEYWORDS:
            if keyword in text_lower:
                details["has_conflict"] = True
                break
        
        return details
