"""Deadline and urgency extraction service."""

import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import dateparser

from models.schemas import Email, ScoreComponent


class DeadlineService:
    """Service for extracting deadlines and calculating urgency scores."""

    # Urgency keywords and their scores
    URGENCY_KEYWORDS = {
        # Critical urgency (15+ points)
        "asap": 20,
        "urgent": 18,
        "emergency": 20,
        "critical": 18,
        "immediately": 20,
        "right away": 18,
        "as soon as possible": 18,
        
        # High urgency (10-14 points)
        "deadline": 14,
        "due today": 15,
        "by end of day": 14,
        "eod": 14,
        "by close of business": 13,
        "cob": 13,
        "time-sensitive": 12,
        "time sensitive": 12,
        "pressing": 11,
        "priority": 10,
        
        # Medium urgency (5-9 points)
        "soon": 7,
        "this week": 8,
        "by friday": 9,
        "by monday": 9,
        "quickly": 6,
        "prompt": 6,
        "timely": 5,
        
        # Low urgency (1-4 points)
        "when you can": 2,
        "when possible": 2,
        "at your convenience": 1,
        "no rush": 0,
        "whenever": 1,
    }

    # Relative time patterns
    RELATIVE_PATTERNS = [
        (r"by\s+(tomorrow|tmrw)", 1),
        (r"by\s+(end\s+of\s+)?today", 0),
        (r"within\s+(\d+)\s+hours?", "hours"),
        (r"within\s+(\d+)\s+days?", "days"),
        (r"in\s+(\d+)\s+hours?", "hours"),
        (r"in\s+(\d+)\s+days?", "days"),
        (r"next\s+week", 7),
        (r"this\s+week", 5),
        (r"by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", "weekday"),
    ]

    def calculate_score(self, email: Email) -> ScoreComponent:
        """Calculate deadline urgency score from email."""
        
        text = f"{email.subject} {email.body}".lower()
        
        # 1. Extract explicit deadlines
        deadline_info = self._extract_deadline(text)
        
        # 2. Calculate keyword-based urgency
        keyword_score, keyword_reason = self._calculate_keyword_urgency(text)
        
        # 3. Calculate deadline-based urgency
        deadline_score = 0
        deadline_reason = ""
        
        if deadline_info:
            deadline_date, deadline_type = deadline_info
            days_until = (deadline_date - datetime.now()).days
            
            if days_until < 0:
                deadline_score = 25  # Overdue!
                deadline_reason = f"OVERDUE by {abs(days_until)} days"
            elif days_until == 0:
                deadline_score = 23
                deadline_reason = "Due TODAY"
            elif days_until == 1:
                deadline_score = 20
                deadline_reason = "Due TOMORROW"
            elif days_until <= 3:
                deadline_score = 16
                deadline_reason = f"Due in {days_until} days"
            elif days_until <= 7:
                deadline_score = 12
                deadline_reason = f"Due in {days_until} days (this week)"
            elif days_until <= 14:
                deadline_score = 8
                deadline_reason = f"Due in {days_until} days"
            else:
                deadline_score = 4
                deadline_reason = f"Due in {days_until} days"
        
        # 4. Combine scores (take higher of the two)
        if deadline_score > keyword_score:
            final_score = min(deadline_score, 25)
            reason = deadline_reason
            confidence = 0.9
        elif keyword_score > 0:
            final_score = min(keyword_score, 25)
            reason = keyword_reason
            confidence = 0.8
        else:
            final_score = 0
            reason = "No urgency indicators detected"
            confidence = 0.7
        
        return ScoreComponent(
            score=final_score,
            max=25,
            reason=reason,
            confidence=confidence
        )

    def extract_due_date(self, text: str) -> Optional[Tuple[datetime, str]]:
        """Extract due date from text. Returns (date, type) where type is 'explicit' or 'relative'."""
        return self._extract_deadline(text)

    def _extract_deadline(self, text: str) -> Optional[Tuple[datetime, str]]:
        """Extract deadline date from text."""
        
        # Try relative patterns first
        for pattern, value in self.RELATIVE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if value == "hours":
                    hours = int(match.group(1))
                    return (datetime.now() + timedelta(hours=hours), "relative")
                elif value == "days":
                    days = int(match.group(1))
                    return (datetime.now() + timedelta(days=days), "relative")
                elif value == "weekday":
                    weekday_name = match.group(1).lower()
                    target_date = self._next_weekday(weekday_name)
                    if target_date:
                        return (target_date, "relative")
                elif isinstance(value, int):
                    return (datetime.now() + timedelta(days=value), "relative")
        
        # Try to find explicit dates using dateparser
        date_patterns = [
            r"by\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
            r"due\s+(?:on\s+)?(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
            r"deadline[:\s]+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
            r"before\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed = dateparser.parse(
                    date_str,
                    settings={
                        'PREFER_DATES_FROM': 'future',
                        'RELATIVE_BASE': datetime.now()
                    }
                )
                if parsed and parsed > datetime.now() - timedelta(days=1):
                    return (parsed, "explicit")
        
        return None

    def _next_weekday(self, weekday_name: str) -> Optional[datetime]:
        """Get next occurrence of a weekday."""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        if weekday_name.lower() not in weekdays:
            return None
        
        target = weekdays[weekday_name.lower()]
        today = datetime.now()
        days_ahead = target - today.weekday()
        
        if days_ahead <= 0:
            days_ahead += 7
        
        return today + timedelta(days=days_ahead)

    def _calculate_keyword_urgency(self, text: str) -> Tuple[int, str]:
        """Calculate urgency score based on keywords."""
        
        max_score = 0
        matched_keyword = ""
        
        for keyword, score in self.URGENCY_KEYWORDS.items():
            if keyword in text:
                if score > max_score:
                    max_score = score
                    matched_keyword = keyword
        
        if max_score > 0:
            return (min(max_score, 25), f"Urgency keyword detected: '{matched_keyword}'")
        
        return (0, "")
