"""API routes for task extraction and management."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.schemas import (
    Task,
    TaskUpdate,
    TaskExtractRequest,
    TaskExtractResponse,
    TaskCompleteResponse,
    Email,
)
from models.database import get_db
from services.task_extractor import TaskExtractorService
from services.scorer import PriorityScorerService

router = APIRouter(prefix="/api/v1/tasks", tags=["Task Extraction"])

# Initialize services
task_service = TaskExtractorService()
scorer_service = PriorityScorerService()


@router.post("/extract", response_model=TaskExtractResponse)
async def extract_tasks(
    request: TaskExtractRequest,
    db: Session = Depends(get_db)
):
    """
    Extract actionable tasks from an email.
    
    Uses NLP to detect action items, deadlines, and requests.
    Tasks inherit priority from the email's priority score.
    """
    try:
        # Get email priority score if not provided
        priority_score = request.email_priority_score
        if priority_score is None:
            score_result = scorer_service.score_email(request.email, db)
            priority_score = score_result.score
        
        result = task_service.extract_tasks(request.email, priority_score, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task extraction failed: {str(e)}")


@router.post("/extract/batch")
async def extract_tasks_batch(
    emails: List[Email],
    db: Session = Depends(get_db)
):
    """
    Extract tasks from multiple emails in batch.
    """
    if not emails:
        raise HTTPException(status_code=400, detail="No emails provided")
    
    if len(emails) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 emails per batch")
    
    try:
        results = task_service.extract_tasks_batch(emails, db)
        return {
            "results": results,
            "total_emails": len(emails),
            "total_tasks": sum(r.task_count for r in results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch extraction failed: {str(e)}")


@router.get("", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed, archived"),
    priority: Optional[str] = Query(None, description="Filter by priority: critical, high, medium, low, minimal"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with optional filtering.
    
    Tasks are sorted by priority score (highest first) and creation date.
    """
    try:
        tasks = task_service.get_tasks(db, status=status, priority=priority, limit=limit)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get a single task by ID."""
    task = task_service.get_task_by_id(db, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a task's properties.
    
    Can update: title, description, due_date, priority, status
    """
    update_dict = updates.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Convert status enum to string if present
    if "status" in update_dict and update_dict["status"]:
        update_dict["status"] = update_dict["status"].value
    
    task = task_service.update_task(db, task_id, update_dict)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.patch("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark a task as complete.
    
    Returns whether the source email should be archived
    (when all tasks from that email are completed).
    """
    result = task_service.complete_task(db, task_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return TaskCompleteResponse(**result)


@router.get("/by-email/{email_id}", response_model=List[Task])
async def get_tasks_by_email(
    email_id: str,
    db: Session = Depends(get_db)
):
    """Get all tasks extracted from a specific email."""
    try:
        tasks = task_service.get_tasks_by_email(db, email_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Delete a task."""
    success = task_service.delete_task(db, task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}
