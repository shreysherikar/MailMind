"""Google Gemini API client wrapper (Replaced by Groq)."""

import json
from typing import Optional, Dict, Any

from config import settings
from shared.groq_client import get_groq_client


class GeminiClient:
    """Wrapper that redirects Gemini calls to Groq (since User wants Groq only)."""

    def __init__(self):
        self.groq = get_groq_client()
        self._initialized = self.groq.is_available
        if not self._initialized:
            print("Warning: Groq API not available (GeminiClient wrapper)")

    @property
    def is_available(self) -> bool:
        """Check if backend (Groq) is available."""
        return self.groq.is_available

    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze emotional tone of email text."""
        if not self.is_available:
            return self._fallback_tone_analysis(text)

        result = self.groq.analyze_tone(text)
        if result:
            return result
        
        return self._fallback_tone_analysis(text)

    def extract_tasks(self, subject: str, body: str) -> list:
        """Extract actionable tasks from email content."""
        if not self.is_available:
            return self._fallback_task_extraction(subject, body)

        result = self.groq.extract_tasks(subject, body)
        if result:
            return result
        
        return self._fallback_task_extraction(subject, body)

    def infer_sender_authority(self, sender_name: str, sender_email: str, signature: str) -> Dict[str, Any]:
        """Infer sender's authority level from email signature and context."""
        if not self.is_available:
            return {"authority_type": "unknown", "confidence": 0.5, "title": None}

        result = self.groq.infer_sender_authority(sender_name, sender_email, signature)
        if result:
            return result
        
        return {"authority_type": "unknown", "confidence": 0.5, "title": None}

    def _fallback_tone_analysis(self, text: str) -> Dict[str, Any]:
        """Rule-based fallback for tone analysis."""
        text_lower = text.lower()
        
        urgency = 0
        stress = 0
        anger = 0
        excitement = 0
        
        # Urgency indicators
        urgent_words = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline', 'today', 'now']
        for word in urgent_words:
            if word in text_lower:
                urgency += 15
        
        # Stress indicators
        stress_words = ['worried', 'concerned', 'issue', 'problem', 'stuck', 'help', 'struggling']
        for word in stress_words:
            if word in text_lower:
                stress += 12
        
        # Anger indicators
        anger_words = ['disappointed', 'unacceptable', 'frustrated', 'complaint', 'terrible', 'worst']
        for word in anger_words:
            if word in text_lower:
                anger += 15
        
        # Excitement indicators
        excitement_words = ['excited', 'great', 'amazing', 'wonderful', 'thrilled', 'congratulations']
        for word in excitement_words:
            if word in text_lower:
                excitement += 15
        
        # Check for exclamation marks and caps
        if text.count('!') > 2:
            urgency += 10
            excitement += 10
        if sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.3:
            urgency += 15
            anger += 10
        
        return {
            "urgency": min(urgency, 100),
            "stress": min(stress, 100),
            "anger": min(anger, 100),
            "excitement": min(excitement, 100),
            "formality": 50,
            "overall_intensity": min((urgency + stress + anger + excitement) // 4, 100)
        }

    def _fallback_task_extraction(self, subject: str, body: str) -> list:
        """Rule-based fallback for task extraction."""
        tasks = []
        text = f"{subject} {body}".lower()
        
        # Common task patterns
        task_patterns = [
            "please review",
            "please send",
            "please update",
            "please complete",
            "please prepare",
            "please schedule",
            "can you",
            "could you",
            "would you",
            "need you to",
            "i need",
            "action required",
            "todo:",
            "task:",
        ]
        
        sentences = body.replace('\n', '. ').split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for pattern in task_patterns:
                if pattern in sentence_lower and len(sentence.strip()) > 10:
                    tasks.append({
                        "title": sentence.strip()[:100],
                        "description": sentence.strip(),
                        "due_date": None,
                        "due_date_type": None,
                        "original_text": sentence.strip(),
                        "confidence": 0.6
                    })
                    break
        
        return tasks[:5]  # Limit to 5 tasks
