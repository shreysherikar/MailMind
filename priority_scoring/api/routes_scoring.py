"""API routes for email priority scoring."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any

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


@router.get("", response_model=List[dict])
async def list_emails(
    limit: int = 100,
    status: str = "inbox",
    db: Session = Depends(get_db)
):
    """
    List stored emails. Default shows only inbox items.
    """
    from shared.database import StoredEmailDB
    
    query = db.query(StoredEmailDB)
    
    if status != "all":
        query = query.filter(StoredEmailDB.status == status)
        
    emails = query.order_by(StoredEmailDB.received_at.desc()).limit(limit).all()
    
    # We might want to return a cleaner schema, but for now dict is fine or reuse Email schema if compatible
    # Let's map to a simple response structure
    return [
        {
            "id": e.id,
            "subject": e.subject,
            "sender_email": e.sender,
            "recipient": e.recipient,
            "timestamp": e.received_at,
            "snippet": e.snippet,
            "body": e.body,
            "score": 0 # We could join with cache if needed, but frontend might fetch scores separately or we just assume they are scored.
            # Actually, the command center needs the SCORE to sort into tabs.
            # Let's fetch the score from cache!
        }
        for e in emails
    ]

# We need to improve the list_emails to include the score.

@router.get("/with-scores", response_model=List[dict])
async def list_emails_with_scores(
    limit: int = 100,
    status: str = "inbox",
    db: Session = Depends(get_db)
):
    """
    List stored emails with their latest scores.
    """
    from shared.database import StoredEmailDB, EmailScoreCache
    
    # Query emails
    query = db.query(StoredEmailDB, EmailScoreCache).outerjoin(
        EmailScoreCache, StoredEmailDB.id == EmailScoreCache.email_id
    )
    
    if status != "all":
        query = query.filter(StoredEmailDB.status == status)
        
    results = query.order_by(StoredEmailDB.received_at.desc()).limit(limit).all()
    
    response = []
    for email, score in results:
        response.append({
            "id": email.id,
            "subject": email.subject,
            "sender": email.sender,
            "recipient": email.recipient,
            "timestamp": email.received_at,
            "snippet": email.snippet,
            "body": email.body,
            "score": score.score if score else 0,
            "priority_label": score.label if score else "unknown",
            "priority_color": score.color if score else "gray",
            "priority_badge": "⚪" # Default
        })
        
        # update badge if score exists (it's not in DB model effectively enough to query easily without joining logic that was in get_priority_level)
        if score:
            # We can rely on frontend to map label to badge or just pass what we have.
            # The cache has 'badge' column? Let's check shared/database.py
             pass
             
    return response


@router.patch("/{email_id}/status")
async def update_email_status(
    email_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update email status (inbox, done, archived, snoozed)."""
    from shared.database import StoredEmailDB
    
    email = db.query(StoredEmailDB).filter(StoredEmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    if status not in ["inbox", "done", "archived", "snoozed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    email.status = status
    db.commit()
    
    return {"message": "Status updated"}


@router.patch("/{email_id}/snooze")
async def snooze_email(
    email_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Snooze an email for a number of hours."""
    from shared.database import StoredEmailDB
    from datetime import datetime, timedelta, timezone
    
    email = db.query(StoredEmailDB).filter(StoredEmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    email.status = "snoozed"
    email.snoozed_until = datetime.now(timezone.utc) + timedelta(hours=hours)
    db.commit()
    
    return {"message": f"Snoozed for {hours} hours"}


@router.patch("/{email_id}/status")
async def update_email_status(
    email_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update email status (inbox, done, archived, snoozed)."""
    from shared.database import StoredEmailDB
    
    email = db.query(StoredEmailDB).filter(StoredEmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    if status not in ["inbox", "done", "archived", "snoozed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    email.status = status
    db.commit()
    
    return {"message": "Status updated"}


@router.patch("/{email_id}/snooze")
async def snooze_email(
    email_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Snooze an email for a number of hours."""
    from shared.database import StoredEmailDB
    from datetime import datetime, timedelta, timezone
    
    email = db.query(StoredEmailDB).filter(StoredEmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    email.status = "snoozed"
    email.snoozed_until = datetime.now(timezone.utc) + timedelta(hours=hours)
    db.commit()
    
    return {"message": f"Snoozed for {hours} hours"}
