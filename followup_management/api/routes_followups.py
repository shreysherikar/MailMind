"""API routes for follow-up management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from followup_management.models.schemas import (
    FollowUp,
    FollowUpUpdate,
    FollowUpDetectRequest,
    FollowUpDetectResponse,
    FollowUpBatchDetectRequest,
    FollowUpBatchDetectResponse,
    ReplyCheckRequest,
    ReplyCheckResponse,
    FollowUpStats,
)
from priority_scoring.models.schemas import Email
from shared.database import get_db
from followup_management.services.followup_detector import FollowUpDetectorService
from followup_management.services.reply_matcher import ReplyMatcherService

router = APIRouter(prefix="/api/v1/followups", tags=["Follow-up Management"])

# Initialize services
followup_service = FollowUpDetectorService()
reply_matcher = ReplyMatcherService()


@router.post("/detect", response_model=FollowUpDetectResponse)
async def detect_followup(
    request: FollowUpDetectRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a sent email to detect if it expects a reply.
    
    Uses AI to detect:
    - Questions asked
    - Requests made
    - Action items assigned to recipient
    - Urgency indicators
    
    If the email expects a reply, creates a follow-up tracking entry.
    """
    try:
        result = followup_service.detect_followup(
            request.email,
            thread_id=request.thread_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Follow-up detection failed: {str(e)}")


@router.post("/detect/batch", response_model=FollowUpBatchDetectResponse)
async def detect_followups_batch(
    request: FollowUpBatchDetectRequest,
    db: Session = Depends(get_db)
):
    """
    Detect follow-ups for multiple sent emails in batch.
    """
    if not request.emails:
        raise HTTPException(status_code=400, detail="No emails provided")
    
    if len(request.emails) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 emails per batch")
    
    try:
        result = followup_service.detect_followups_batch(request.emails, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")


@router.get("", response_model=List[FollowUp])
async def get_followups(
    status: Optional[str] = Query(None, description="Filter by status: waiting, replied, overdue, no_reply_needed, archived"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all follow-ups with optional status filtering.
    
    Follow-ups are sorted by sent date (most recent first).
    """
    try:
        followups = followup_service.get_followups(db, status=status, limit=limit)
        return followups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get follow-ups: {str(e)}")


@router.get("/waiting", response_model=List[FollowUp])
async def get_waiting_followups(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all follow-ups still waiting for a reply.
    
    Includes both 'waiting' and 'overdue' status items.
    Sorted by sent date (oldest first) to show most urgent.
    """
    try:
        followups = followup_service.get_waiting_followups(db, limit=limit)
        return followups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get waiting follow-ups: {str(e)}")


@router.get("/overdue", response_model=List[FollowUp])
async def get_overdue_followups(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get follow-ups that are overdue for a reply.
    
    Sorted by days waiting (longest first).
    """
    try:
        followups = followup_service.get_overdue_followups(db, limit=limit)
        return followups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overdue follow-ups: {str(e)}")


@router.get("/stats", response_model=FollowUpStats)
async def get_followup_stats(
    db: Session = Depends(get_db)
):
    """
    Get follow-up statistics.
    
    Returns counts for each status and average response time.
    """
    try:
        stats = followup_service.get_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/{followup_id}", response_model=FollowUp)
async def get_followup(
    followup_id: str,
    db: Session = Depends(get_db)
):
    """Get a single follow-up by ID."""
    
    followup = followup_service.get_followup_by_id(db, followup_id)
    
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return followup


@router.patch("/{followup_id}", response_model=FollowUp)
async def update_followup(
    followup_id: str,
    updates: FollowUpUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a follow-up's properties.
    
    Can update: status, expected_reply_by, reply_email_id, reply_subject, replied_at
    """
    update_dict = updates.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Convert status enum to string if present
    if "status" in update_dict and update_dict["status"]:
        update_dict["status"] = update_dict["status"].value
    
    followup = followup_service.update_followup(db, followup_id, update_dict)
    
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return followup


@router.patch("/{followup_id}/replied", response_model=FollowUp)
async def mark_followup_replied(
    followup_id: str,
    reply_email_id: str = Query(..., description="ID of the reply email"),
    reply_subject: Optional[str] = Query(None, description="Subject of the reply"),
    db: Session = Depends(get_db)
):
    """
    Mark a follow-up as replied.
    
    Updates status to 'replied' and records the reply email information.
    """
    followup = followup_service.mark_as_replied(
        db, followup_id, reply_email_id, reply_subject
    )
    
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return followup


@router.delete("/{followup_id}")
async def delete_followup(
    followup_id: str,
    db: Session = Depends(get_db)
):
    """Delete a follow-up."""
    
    success = followup_service.delete_followup(db, followup_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return {"message": "Follow-up deleted successfully"}


@router.post("/check-reply", response_model=ReplyCheckResponse)
async def check_if_reply(
    request: ReplyCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if an incoming email is a reply to a tracked follow-up.
    
    Uses multiple matching strategies:
    - Thread ID matching (if provided)
    - Subject line matching (Re: pattern)
    - Sender/recipient matching
    
    If a match is found, automatically updates the follow-up status to 'replied'.
    """
    try:
        result = reply_matcher.check_if_reply(
            request.email,
            thread_id=request.thread_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply check failed: {str(e)}")


@router.post("/find-matches", response_model=List[FollowUp])
async def find_potential_matches(
    email: Email,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Find potential follow-up matches for an incoming email.
    
    Returns a ranked list of possible matches without updating their status.
    Useful for manual confirmation before marking as replied.
    """
    try:
        matches = reply_matcher.find_potential_matches(email, db, limit=limit)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find matches: {str(e)}")
