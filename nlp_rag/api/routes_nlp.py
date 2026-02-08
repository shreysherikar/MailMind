"""API routes for NLP features."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from priority_scoring.models.schemas import Email
from nlp_rag.models.schemas import NLPAnalysis, EmailSummary
from nlp_rag.services.nlp_analyzer import get_nlp_analyzer

router = APIRouter(prefix="/api/v1/nlp", tags=["NLP Analysis"])


@router.post("/analyze", response_model=NLPAnalysis)
async def analyze_email(email: Email):
    """
    Perform complete NLP analysis on an email.
    
    Includes:
    - Email summarization
    - Sentiment analysis
    - Intent detection
    - Named entity extraction
    - Readability scoring
    """
    analyzer = get_nlp_analyzer()
    
    try:
        analysis = analyzer.analyze_email(
            email_id=email.id,
            subject=email.subject,
            body=email.body,
            sender=email.sender_email
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/summarize", response_model=EmailSummary)
async def summarize_email(email: Email):
    """
    Generate a comprehensive summary of an email.
    
    Returns:
    - Short one-line summary
    - Detailed 2-3 sentence summary
    - Key points as bullet list
    - Action items extracted
    - Named entities found
    - Detected intent
    """
    analyzer = get_nlp_analyzer()
    
    try:
        summary = analyzer.summarize_email(
            email_id=email.id,
            subject=email.subject,
            body=email.body
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/entities")
async def extract_entities(email: Email):
    """
    Extract named entities from an email.
    
    Extracts:
    - People (names, email addresses)
    - Organizations (companies)
    - Dates
    - Locations
    - Money amounts
    - Projects
    - Products
    """
    analyzer = get_nlp_analyzer()
    
    try:
        entities = analyzer.extract_entities(email.subject, email.body)
        return {
            "email_id": email.id,
            "entities": entities,
            "count": len(entities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.post("/intent")
async def detect_intent(email: Email):
    """
    Detect the primary intent of an email.
    
    Possible intents:
    - request: Asking for something
    - question: Seeking information
    - information: Sharing information
    - complaint: Expressing dissatisfaction
    - meeting: Scheduling or discussing meetings
    - followup: Following up on previous communication
    - acknowledgment: Confirming receipt or understanding
    - unknown: Cannot determine intent
    """
    analyzer = get_nlp_analyzer()
    
    try:
        intent = analyzer.detect_intent(email.subject, email.body)
        return {
            "email_id": email.id,
            "intent": intent,
            "subject": email.subject
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent detection failed: {str(e)}")
