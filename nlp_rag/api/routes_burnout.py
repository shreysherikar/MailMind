"""API routes for burnout detection."""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from nlp_rag.models.schemas import BurnoutMetrics
from nlp_rag.services.burnout_detector import get_burnout_detector

router = APIRouter(prefix="/api/v1/burnout", tags=["Burnout Detection"])


class EmailForAnalysis(BaseModel):
    """Email data for burnout analysis."""
    id: str
    subject: str
    body: str
    date: datetime
    sender: str
    is_sent: bool = False  # True if user sent this email


class BurnoutAnalysisRequest(BaseModel):
    """Request for burnout analysis."""
    user_email: str
    emails: List[EmailForAnalysis]
    period_days: int = 30


@router.post("/analyze", response_model=BurnoutMetrics)
async def analyze_burnout(request: BurnoutAnalysisRequest):
    """
    Analyze email patterns for burnout signals.
    
    This is MailMind's boldest feature - detecting burnout before it happens.
    
    Analyzes:
    - Late-night email habits (after 10 PM)
    - Weekend work patterns
    - Email volume and workload
    - Sentiment and stress levels in communications
    - Response time patterns
    
    Returns:
    - Risk score (0-100)
    - Risk level (low, moderate, high, critical)
    - Specific signals detected
    - Actionable recommendations
    
    Note: This is about early help, not surveillance. All analysis is
    private and designed to support employee wellbeing.
    """
    detector = get_burnout_detector()
    
    try:
        # Convert to dict format expected by detector
        emails_data = [
            {
                "id": email.id,
                "subject": email.subject,
                "body": email.body,
                "date": email.date,
                "sender": email.sender,
                "is_sent": email.is_sent
            }
            for email in request.emails
        ]
        
        metrics = detector.analyze_user_patterns(
            user_email=request.user_email,
            emails=emails_data,
            period_days=request.period_days
        )
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Burnout analysis failed: {str(e)}")


@router.post("/quick-check")
async def quick_burnout_check(request: BurnoutAnalysisRequest):
    """
    Quick burnout check with simplified response.
    
    Returns just the risk level and top recommendations without
    detailed metrics.
    """
    detector = get_burnout_detector()
    
    try:
        emails_data = [
            {
                "id": email.id,
                "subject": email.subject,
                "body": email.body,
                "date": email.date,
                "sender": email.sender,
                "is_sent": email.is_sent
            }
            for email in request.emails
        ]
        
        metrics = detector.analyze_user_patterns(
            user_email=request.user_email,
            emails=emails_data,
            period_days=request.period_days
        )
        
        return {
            "user_email": request.user_email,
            "risk_level": metrics.risk_level,
            "risk_score": metrics.risk_score,
            "signals_detected": len(metrics.signals),
            "top_recommendation": metrics.recommendations[0] if metrics.recommendations else None,
            "period_days": request.period_days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick check failed: {str(e)}")


@router.get("/info")
async def burnout_detection_info():
    """
    Get information about burnout detection feature.
    
    Returns details about what signals are detected and how the
    analysis works.
    """
    return {
        "feature": "Burnout Detection",
        "description": "AI-powered early detection of burnout signals from email patterns",
        "signals_detected": [
            {
                "name": "Late Night Emails",
                "description": "Emails sent after 10 PM or before 6 AM",
                "threshold": "More than 5 in analysis period"
            },
            {
                "name": "Weekend Work",
                "description": "Emails sent on Saturdays or Sundays",
                "threshold": "More than 3 in analysis period"
            },
            {
                "name": "High Volume",
                "description": "Excessive number of emails per day",
                "threshold": "More than 50 emails per day average"
            },
            {
                "name": "Negative Sentiment",
                "description": "Consistently negative tone in communications",
                "threshold": "Average sentiment below -0.3"
            },
            {
                "name": "Stress Language",
                "description": "High stress indicators in email content",
                "threshold": "Average stress level above 60/100"
            },
            {
                "name": "Response Delay",
                "description": "Increasing response times (may indicate overwhelm)",
                "threshold": "Average response time over 48 hours"
            }
        ],
        "risk_levels": {
            "low": "0-24: Healthy email patterns",
            "moderate": "25-49: Some signals present, monitor",
            "high": "50-74: Multiple signals, take action",
            "critical": "75-100: Urgent attention needed"
        },
        "privacy_note": "All analysis is private and designed for early help, not surveillance"
    }
