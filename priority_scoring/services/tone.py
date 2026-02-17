"""Emotional tone analysis service."""

from typing import Optional, Dict, Any

from models.schemas import Email, ScoreComponent
from .groq_client import GroqClient, get_groq_client


class ToneService:
    """Service for analyzing emotional tone of emails."""

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.groq = groq_client or get_groq_client()

    def calculate_score(self, email: Email) -> ScoreComponent:
        """Calculate emotional tone score from email."""
        
        text = f"{email.subject}\n\n{email.body}"
        
        # Get tone analysis (from Groq or fallback)
        tone_data = self.groq.analyze_tone(text)
        
        # Calculate weighted score from tone components
        score = self._calculate_tone_score(tone_data)
        reason = self._generate_reason(tone_data)
        confidence = self._calculate_confidence(tone_data)
        
        return ScoreComponent(
            score=min(score, 20),
            max=20,
            reason=reason,
            confidence=confidence
        )

    def _calculate_tone_score(self, tone_data: Dict[str, Any]) -> int:
        """Calculate priority score from tone analysis."""
        
        urgency = tone_data.get("urgency", 0)
        stress = tone_data.get("stress", 0)
        anger = tone_data.get("anger", 0)
        excitement = tone_data.get("excitement", 0)
        overall_intensity = tone_data.get("overall_intensity", 0)
        
        # Weight the components
        # Urgency and stress are most important for priority
        weighted_score = (
            urgency * 0.35 +
            stress * 0.25 +
            anger * 0.20 +
            overall_intensity * 0.15 +
            excitement * 0.05
        )
        
        # Scale to 0-20 range
        score = int((weighted_score / 100) * 20)
        
        return max(0, min(score, 20))

    def _generate_reason(self, tone_data: Dict[str, Any]) -> str:
        """Generate human-readable reason for the tone score."""
        
        urgency = tone_data.get("urgency", 0)
        stress = tone_data.get("stress", 0)
        anger = tone_data.get("anger", 0)
        excitement = tone_data.get("excitement", 0)
        
        indicators = []
        
        if urgency >= 70:
            indicators.append("high urgency")
        elif urgency >= 40:
            indicators.append("moderate urgency")
        
        if stress >= 70:
            indicators.append("high stress")
        elif stress >= 40:
            indicators.append("some stress")
        
        if anger >= 60:
            indicators.append("frustration detected")
        elif anger >= 30:
            indicators.append("mild frustration")
        
        if excitement >= 70:
            indicators.append("high excitement")
        elif excitement >= 40:
            indicators.append("positive tone")
        
        if not indicators:
            return "Neutral tone detected"
        
        return f"Tone: {', '.join(indicators)}"

    def _calculate_confidence(self, tone_data: Dict[str, Any]) -> float:
        """Calculate confidence based on whether AI or fallback was used."""
        
        # If we got detailed analysis, higher confidence
        if all(key in tone_data for key in ["urgency", "stress", "anger", "excitement", "formality"]):
            return 0.85 if self.groq.is_available else 0.65
        
        return 0.5

    def get_detailed_analysis(self, email: Email) -> Dict[str, Any]:
        """Get detailed tone analysis for debugging/display."""
        
        text = f"{email.subject}\n\n{email.body}"
        tone_data = self.groq.analyze_tone(text)
        
        return {
            "raw_scores": tone_data,
            "priority_score": self._calculate_tone_score(tone_data),
            "summary": self._generate_reason(tone_data),
            "api_available": self.groq.is_available
        }
