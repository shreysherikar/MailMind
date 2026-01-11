"""API routes for email priority scoring."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.schemas import (
    EmailScoreRequest,
    EmailScoreBatchRequest,
    PriorityScore,
    PriorityScoreBatchResponse,
)
from models.database import get_db
from services.scorer import PriorityScorerService

router = APIRouter(prefix="/api/v1/emails", tags=["Priority Scoring"])

# Initialize service
scorer_service = PriorityScorerService()


@router.post("/score", response_model=PriorityScore)
async def score_email(
    request: EmailScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Score a single email and return priority score with breakdown.
    
    Returns a priority score (0-100) with:
    - Color-coded badge (red/orange/yellow/green/gray)
    - Detailed breakdown of each scoring component
    - Confidence level
    """
    try:
        score = scorer_service.score_email(request.email, db)
        return score
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/score/batch", response_model=PriorityScoreBatchResponse)
async def score_emails_batch(
    request: EmailScoreBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Score multiple emails in batch.
    
    Returns scores for all emails plus aggregate statistics.
    """
    if not request.emails:
        raise HTTPException(status_code=400, detail="No emails provided")
    
    if len(request.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per batch")
    
    try:
        result = scorer_service.score_emails_batch(request.emails, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")


@router.post("/score/explain")
async def explain_score(
    request: EmailScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Score an email and return a human-readable explanation.
    
    Useful for debugging and understanding why an email received its score.
    """
    try:
        score = scorer_service.score_email(request.email, db)
        explanation = scorer_service.get_score_explanation(score)
        
        return {
            "score": score,
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")
