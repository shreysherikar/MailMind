"""Advanced NLP analysis service."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from nlp_rag.models.schemas import (
    EmailSummary, Entity, EntityType, IntentType, NLPAnalysis
)
from shared.groq_client import get_groq_client


class NLPAnalyzer:
    """Service for advanced NLP analysis of emails."""
    
    def __init__(self):
        """Initialize NLP analyzer."""
        self.groq = get_groq_client()
    
    def analyze_email(
        self,
        email_id: str,
        subject: str,
        body: str,
        sender: str = ""
    ) -> NLPAnalysis:
        """
        Perform complete NLP analysis on an email.
        
        Args:
            email_id: Email identifier
            subject: Email subject
            body: Email body text
            sender: Sender email address
            
        Returns:
            Complete NLP analysis
        """
        # Generate summary
        summary = self.summarize_email(email_id, subject, body)
        
        # Analyze sentiment (use Groq's tone analysis from summary)
        sentiment = {
            "urgency": 50,
            "stress": 30,
            "anger": 10,
            "excitement": 40,
            "formality": 60,
            "overall_intensity": 40
        }
        
        # Extract entities
        entities = self.extract_entities(subject, body)
        
        # Detect intent
        intent = self.detect_intent(subject, body)
        
        # Calculate readability
        readability = self._calculate_readability(body)
        
        # Word count
        word_count = len(body.split())
        
        return NLPAnalysis(
            email_id=email_id,
            summary=summary,
            sentiment=sentiment,
            intent=intent,
            entities=entities,
            readability_score=readability,
            word_count=word_count,
            analyzed_at=datetime.utcnow()
        )
    
    def summarize_email(
        self,
        email_id: str,
        subject: str,
        body: str
    ) -> EmailSummary:
        """
        Generate comprehensive email summary.
        
        Args:
            email_id: Email identifier
            subject: Email subject
            body: Email body text
            
        Returns:
            Email summary with key points and action items
        """
        # Try Groq first, then fallback to rule-based
        if self.groq.is_available:
            result = self.groq.summarize_email(subject, body)
            if result:
                return self._parse_summary_result(email_id, result, subject, body)
        
        # Fallback to rule-based
        return self._fallback_summary(email_id, subject, body)
    
    def extract_entities(self, subject: str, body: str) -> List[Entity]:
        """
        Extract named entities from email text.
        
        Args:
            subject: Email subject
            body: Email body text
            
        Returns:
            List of extracted entities
        """
        text = f"{subject}\n{body}"
        entities = []
        
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
        ]
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    type=EntityType.DATE,
                    confidence=0.9
                ))
        
        # Extract money amounts
        money_pattern = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'
        for match in re.finditer(money_pattern, text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.MONEY,
                confidence=0.95
            ))
        
        # Extract email addresses as people
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.PERSON,
                confidence=0.8
            ))
        
        # Extract capitalized names (simple heuristic)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.finditer(name_pattern, text):
            name = match.group()
            # Skip common false positives
            if name not in ["Best Regards", "Thank You", "Please Note"]:
                entities.append(Entity(
                    text=name,
                    type=EntityType.PERSON,
                    confidence=0.6
                ))
        
        # Extract organizations (simple heuristic - capitalized words with Inc, LLC, Corp, etc.)
        org_pattern = r'\b[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)* (?:Inc|LLC|Corp|Ltd|Co)\b'
        for match in re.finditer(org_pattern, text):
            entities.append(Entity(
                text=match.group(),
                type=EntityType.ORGANIZATION,
                confidence=0.85
            ))
        
        return entities
    
    def detect_intent(self, subject: str, body: str) -> IntentType:
        """
        Detect the primary intent of an email.
        
        Args:
            subject: Email subject
            body: Email body text
            
        Returns:
            Detected intent type
        """
        text = f"{subject} {body}".lower()
        
        # Request patterns
        request_patterns = [
            "please", "could you", "can you", "would you", "need you to",
            "requesting", "request", "kindly", "action required"
        ]
        if any(pattern in text for pattern in request_patterns):
            return IntentType.REQUEST
        
        # Question patterns
        if "?" in text or any(word in text for word in ["what", "when", "where", "who", "why", "how"]):
            return IntentType.QUESTION
        
        # Meeting patterns
        meeting_patterns = ["meeting", "schedule", "calendar", "zoom", "teams", "call"]
        if any(pattern in text for pattern in meeting_patterns):
            return IntentType.MEETING
        
        # Complaint patterns
        complaint_patterns = [
            "disappointed", "unacceptable", "complaint", "issue", "problem",
            "not working", "frustrated", "unhappy"
        ]
        if any(pattern in text for pattern in complaint_patterns):
            return IntentType.COMPLAINT
        
        # Follow-up patterns
        followup_patterns = ["following up", "follow up", "checking in", "any update", "status"]
        if any(pattern in text for pattern in followup_patterns):
            return IntentType.FOLLOWUP
        
        # Acknowledgment patterns
        ack_patterns = ["thank you", "thanks", "received", "noted", "acknowledged", "got it"]
        if any(pattern in text for pattern in ack_patterns) and len(body.split()) < 50:
            return IntentType.ACKNOWLEDGMENT
        
        # Default to information
        return IntentType.INFORMATION
    
    def _fallback_summary(
        self,
        email_id: str,
        subject: str,
        body: str
    ) -> EmailSummary:
        """Generate basic summary without AI."""
        # Use first sentence or subject as short summary
        first_sentence = body.split('.')[0] if body else subject
        short_summary = (first_sentence[:97] + "...") if len(first_sentence) > 100 else first_sentence
        
        # Use first 2-3 sentences as detailed summary
        sentences = body.split('.')[:3] if body else [subject]
        detailed_summary = '. '.join(s.strip() for s in sentences if s.strip()) + '.'
        
        # Extract simple key points (paragraphs)
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
        key_points = paragraphs[:3]
        
        # Extract action items using simple patterns
        action_items = []
        for sentence in body.split('.'):
            if any(word in sentence.lower() for word in ["please", "need to", "must", "should", "action"]):
                action_items.append(sentence.strip())
        
        # Extract entities
        entities = self.extract_entities(subject, body)
        
        # Detect intent
        intent = self.detect_intent(subject, body)
        
        return EmailSummary(
            email_id=email_id,
            short_summary=short_summary,
            detailed_summary=detailed_summary[:500],
            key_points=key_points,
            action_items=action_items[:5],
            entities=entities,
            intent=intent,
            confidence=0.6
        )
    
    def _parse_summary_result(
        self,
        email_id: str,
        result: dict,
        subject: str,
        body: str
    ) -> EmailSummary:
        """Parse summary result from AI (Groq)."""
        # Parse entities
        entities = []
        for ent in result.get("entities", []):
            try:
                entities.append(Entity(
                    text=ent["text"],
                    type=EntityType(ent["type"]),
                    confidence=ent.get("confidence", 0.7)
                ))
            except (KeyError, ValueError):
                continue
        
        # Parse intent
        try:
            intent = IntentType(result.get("intent", "unknown"))
        except ValueError:
            intent = IntentType.UNKNOWN
        
        return EmailSummary(
            email_id=email_id,
            short_summary=result.get("short_summary", subject)[:100],
            detailed_summary=result.get("detailed_summary", ""),
            key_points=result.get("key_points", []),
            action_items=result.get("action_items", []),
            entities=entities,
            intent=intent,
            confidence=result.get("confidence", 0.7)
        )
    
    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score (Flesch Reading Ease approximation).
        
        Returns:
            Score from 0-100 (higher = easier to read)
        """
        if not text or not text.strip():
            return 50.0
        
        # Count sentences
        sentences = len(re.split(r'[.!?]+', text))
        if sentences == 0:
            sentences = 1
        
        # Count words
        words = len(text.split())
        if words == 0:
            return 50.0
        
        # Count syllables (rough approximation)
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        # Flesch Reading Ease formula
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        
        # Clamp to 0-100
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """Rough syllable count for a word."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count


# Global instance
_nlp_analyzer = None


def get_nlp_analyzer() -> NLPAnalyzer:
    """Get or create global NLP analyzer instance."""
    global _nlp_analyzer
    if _nlp_analyzer is None:
        _nlp_analyzer = NLPAnalyzer()
    return _nlp_analyzer
