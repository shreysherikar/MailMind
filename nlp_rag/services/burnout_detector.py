"""Burnout detection service for analyzing email patterns."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

from nlp_rag.models.schemas import BurnoutMetrics, BurnoutSignal
from shared.gemini_client import GeminiClient


class BurnoutDetector:
    """Service for detecting burnout signals from email patterns."""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """Initialize burnout detector."""
        self.gemini = gemini_client or GeminiClient()
    
    def analyze_user_patterns(
        self,
        user_email: str,
        emails: List[Dict[str, Any]],
        period_days: int = 30
    ) -> BurnoutMetrics:
        """
        Analyze email patterns for burnout signals.
        
        Args:
            user_email: User's email address
            emails: List of email dicts with keys: id, subject, body, date, sender, is_sent
            period_days: Analysis period in days
            
        Returns:
            Burnout metrics and recommendations
        """
        if not emails:
            return self._empty_metrics(user_email, period_days)
        
        # Filter emails within period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        period_emails = [
            e for e in emails
            if isinstance(e.get("date"), datetime) and start_date <= e["date"] <= end_date
        ]
        
        if not period_emails:
            return self._empty_metrics(user_email, period_days)
        
        # Separate sent and received
        sent_emails = [e for e in period_emails if e.get("is_sent", False)]
        received_emails = [e for e in period_emails if not e.get("is_sent", False)]
        
        # Calculate email patterns
        late_night_count = self._count_late_night_emails(sent_emails)
        weekend_count = self._count_weekend_emails(sent_emails)
        daily_avg = len(period_emails) / period_days
        
        # Calculate sentiment metrics
        sentiment_scores = []
        stress_scores = []
        
        for email in period_emails:
            text = f"{email.get('subject', '')} {email.get('body', '')}"
            tone = self.gemini.analyze_tone(text)
            
            # Calculate overall sentiment (-1 to 1)
            sentiment = (
                tone.get("excitement", 0) - tone.get("anger", 0) - tone.get("stress", 0)
            ) / 100.0
            sentiment_scores.append(sentiment)
            stress_scores.append(tone.get("stress", 0))
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        avg_stress = sum(stress_scores) / len(stress_scores) if stress_scores else 0.0
        negative_ratio = len([s for s in sentiment_scores if s < -0.2]) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # Calculate response time for sent emails
        avg_response_time = self._calculate_avg_response_time(sent_emails, received_emails)
        
        # Find peak day
        daily_counts = defaultdict(int)
        for email in period_emails:
            date_key = email["date"].date()
            daily_counts[date_key] += 1
        peak_day_count = max(daily_counts.values()) if daily_counts else 0
        
        # Detect signals
        signals = self._detect_signals(
            late_night_count=late_night_count,
            weekend_count=weekend_count,
            daily_avg=daily_avg,
            avg_sentiment=avg_sentiment,
            avg_stress=avg_stress,
            negative_ratio=negative_ratio,
            avg_response_time=avg_response_time
        )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            signals=signals,
            late_night_count=late_night_count,
            weekend_count=weekend_count,
            daily_avg=daily_avg,
            avg_stress=avg_stress,
            negative_ratio=negative_ratio
        )
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(signals, risk_level)
        
        return BurnoutMetrics(
            user_email=user_email,
            period_start=start_date,
            period_end=end_date,
            total_emails_sent=len(sent_emails),
            total_emails_received=len(received_emails),
            late_night_count=late_night_count,
            weekend_count=weekend_count,
            avg_response_time_hours=avg_response_time,
            avg_sentiment_score=avg_sentiment,
            stress_level=avg_stress,
            negative_email_ratio=negative_ratio,
            daily_email_avg=daily_avg,
            peak_day_count=peak_day_count,
            signals=signals,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _count_late_night_emails(self, emails: List[Dict[str, Any]]) -> int:
        """Count emails sent after 10 PM or before 6 AM."""
        count = 0
        for email in emails:
            date = email.get("date")
            if isinstance(date, datetime):
                hour = date.hour
                if hour >= 22 or hour < 6:
                    count += 1
        return count
    
    def _count_weekend_emails(self, emails: List[Dict[str, Any]]) -> int:
        """Count emails sent on weekends (Saturday or Sunday)."""
        count = 0
        for email in emails:
            date = email.get("date")
            if isinstance(date, datetime):
                # weekday() returns 5 for Saturday, 6 for Sunday
                if date.weekday() >= 5:
                    count += 1
        return count
    
    def _calculate_avg_response_time(
        self,
        sent_emails: List[Dict[str, Any]],
        received_emails: List[Dict[str, Any]]
    ) -> float:
        """Calculate average response time in hours."""
        if not sent_emails or not received_emails:
            return 0.0
        
        response_times = []
        
        # Simple heuristic: match received emails to sent emails by subject similarity
        for sent in sent_emails:
            sent_date = sent.get("date")
            sent_subject = sent.get("subject", "").lower()
            
            if not isinstance(sent_date, datetime):
                continue
            
            # Look for received emails after this sent email with similar subject
            for received in received_emails:
                received_date = received.get("date")
                received_subject = received.get("subject", "").lower()
                
                if not isinstance(received_date, datetime):
                    continue
                
                # Check if received is after sent and subject matches
                if received_date > sent_date:
                    # Simple subject matching (contains key words)
                    sent_words = set(sent_subject.split())
                    received_words = set(received_subject.split())
                    overlap = len(sent_words & received_words)
                    
                    if overlap >= 2:  # At least 2 words match
                        time_diff = (received_date - sent_date).total_seconds() / 3600  # hours
                        response_times.append(time_diff)
                        break
        
        return sum(response_times) / len(response_times) if response_times else 24.0
    
    def _detect_signals(
        self,
        late_night_count: int,
        weekend_count: int,
        daily_avg: float,
        avg_sentiment: float,
        avg_stress: float,
        negative_ratio: float,
        avg_response_time: float
    ) -> List[BurnoutSignal]:
        """Detect burnout signals based on metrics."""
        signals = []
        
        # Late night work
        if late_night_count > 5:
            signals.append(BurnoutSignal.LATE_NIGHT_EMAILS)
        
        # Weekend work
        if weekend_count > 3:
            signals.append(BurnoutSignal.WEEKEND_WORK)
        
        # High volume
        if daily_avg > 50:
            signals.append(BurnoutSignal.HIGH_VOLUME)
        
        # Negative sentiment
        if avg_sentiment < -0.3:
            signals.append(BurnoutSignal.NEGATIVE_SENTIMENT)
        
        # High stress
        if avg_stress > 60:
            signals.append(BurnoutSignal.STRESS_LANGUAGE)
        
        # Slow responses (might indicate overwhelm)
        if avg_response_time > 48:
            signals.append(BurnoutSignal.RESPONSE_DELAY)
        
        return signals
    
    def _calculate_risk_score(
        self,
        signals: List[BurnoutSignal],
        late_night_count: int,
        weekend_count: int,
        daily_avg: float,
        avg_stress: float,
        negative_ratio: float
    ) -> float:
        """Calculate overall burnout risk score (0-100)."""
        score = 0.0
        
        # Base score from number of signals
        score += len(signals) * 10
        
        # Late night work (max 20 points)
        score += min(late_night_count * 2, 20)
        
        # Weekend work (max 15 points)
        score += min(weekend_count * 3, 15)
        
        # High volume (max 20 points)
        if daily_avg > 30:
            score += min((daily_avg - 30) * 0.5, 20)
        
        # Stress level (max 20 points)
        score += (avg_stress / 100) * 20
        
        # Negative sentiment (max 15 points)
        score += negative_ratio * 15
        
        return min(score, 100.0)
    
    def _generate_recommendations(
        self,
        signals: List[BurnoutSignal],
        risk_level: str
    ) -> List[str]:
        """Generate actionable recommendations based on signals."""
        recommendations = []
        
        if BurnoutSignal.LATE_NIGHT_EMAILS in signals:
            recommendations.append(
                "Consider setting email boundaries: avoid sending emails after 9 PM"
            )
        
        if BurnoutSignal.WEEKEND_WORK in signals:
            recommendations.append(
                "Try to disconnect on weekends to recharge and prevent burnout"
            )
        
        if BurnoutSignal.HIGH_VOLUME in signals:
            recommendations.append(
                "Your email volume is high. Consider delegating or using filters to reduce load"
            )
        
        if BurnoutSignal.NEGATIVE_SENTIMENT in signals:
            recommendations.append(
                "Detected negative sentiment patterns. Consider taking breaks or discussing workload with your manager"
            )
        
        if BurnoutSignal.STRESS_LANGUAGE in signals:
            recommendations.append(
                "High stress detected in communications. Consider stress management techniques or seeking support"
            )
        
        if BurnoutSignal.RESPONSE_DELAY in signals:
            recommendations.append(
                "Response times are increasing. This might indicate overwhelm - consider prioritizing or asking for help"
            )
        
        # General recommendations based on risk level
        if risk_level == "critical":
            recommendations.append(
                "⚠️ CRITICAL: Multiple burnout signals detected. Please consider discussing workload with your manager or HR"
            )
        elif risk_level == "high":
            recommendations.append(
                "High burnout risk detected. Take proactive steps to manage workload and stress"
            )
        elif risk_level == "moderate":
            recommendations.append(
                "Some burnout signals present. Monitor your work-life balance and take preventive action"
            )
        
        if not recommendations:
            recommendations.append(
                "Your email patterns look healthy. Keep maintaining good work-life balance!"
            )
        
        return recommendations
    
    def _empty_metrics(self, user_email: str, period_days: int) -> BurnoutMetrics:
        """Return empty metrics when no data available."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        return BurnoutMetrics(
            user_email=user_email,
            period_start=start_date,
            period_end=end_date,
            total_emails_sent=0,
            total_emails_received=0,
            late_night_count=0,
            weekend_count=0,
            avg_response_time_hours=0.0,
            avg_sentiment_score=0.0,
            stress_level=0.0,
            negative_email_ratio=0.0,
            daily_email_avg=0.0,
            peak_day_count=0,
            signals=[],
            risk_score=0.0,
            risk_level="low",
            recommendations=["No email data available for analysis"]
        )


# Global instance
_burnout_detector = None


def get_burnout_detector() -> BurnoutDetector:
    """Get or create global burnout detector instance."""
    global _burnout_detector
    if _burnout_detector is None:
        _burnout_detector = BurnoutDetector()
    return _burnout_detector
