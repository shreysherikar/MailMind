"""Smart task extraction service."""

from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy.orm import Session

from models.schemas import (
    Email, Task, TaskExtractResponse, SourceEmail, TaskStatus
)
from models.database import TaskDB
from config import get_priority_level
from .groq_client import GroqClient, get_groq_client
from .deadline import DeadlineService


class TaskExtractorService:
    """Service for extracting actionable tasks from emails."""

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.groq = groq_client or get_groq_client()
        self.deadline_service = DeadlineService()

    def extract_tasks(
        self,
        email: Email,
        email_priority_score: Optional[int] = None,
        db: Optional[Session] = None
    ) -> TaskExtractResponse:
        """Extract tasks from an email."""
        
        # Get raw task data from Groq or fallback
        raw_tasks = self.groq.extract_tasks(email.subject, email.body)
        
        # Convert to Task objects
        tasks = []
        for raw_task in raw_tasks:
            task = self._create_task(raw_task, email, email_priority_score)
            tasks.append(task)
            
            # Save to database if available
            if db:
                self._save_task_to_db(db, task)
        
        return TaskExtractResponse(
            tasks=tasks,
            task_count=len(tasks),
            source_email_id=email.id
        )

    def extract_tasks_batch(
        self,
        emails: List[Email],
        db: Optional[Session] = None
    ) -> List[TaskExtractResponse]:
        """Extract tasks from multiple emails."""
        
        responses = []
        for email in emails:
            response = self.extract_tasks(email, db=db)
            responses.append(response)
        
        return responses

    def get_tasks(
        self,
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks from database with optional filters."""
        
        query = db.query(TaskDB)
        
        if status:
            query = query.filter(TaskDB.status == status)
        
        if priority:
            query = query.filter(TaskDB.priority == priority)
        
        query = query.order_by(TaskDB.priority_score.desc(), TaskDB.created_at.desc())
        query = query.limit(limit)
        
        db_tasks = query.all()
        
        return [self._db_to_task(db_task) for db_task in db_tasks]

    def get_task_by_id(self, db: Session, task_id: str) -> Optional[Task]:
        """Get a single task by ID."""
        
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        
        if not db_task:
            return None
        
        return self._db_to_task(db_task)

    def get_tasks_by_email(self, db: Session, email_id: str) -> List[Task]:
        """Get all tasks extracted from a specific email."""
        
        db_tasks = db.query(TaskDB).filter(
            TaskDB.source_email_id == email_id
        ).all()
        
        return [self._db_to_task(db_task) for db_task in db_tasks]

    def update_task(
        self,
        db: Session,
        task_id: str,
        updates: dict
    ) -> Optional[Task]:
        """Update a task."""
        
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        
        if not db_task:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(db_task, key) and value is not None:
                setattr(db_task, key, value)
        
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
        
        return self._db_to_task(db_task)

    def complete_task(self, db: Session, task_id: str) -> dict:
        """Mark a task as complete and check if email should be archived."""
        
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        
        if not db_task:
            return {"error": "Task not found"}
        
        # Mark as completed
        db_task.status = TaskStatus.COMPLETED.value
        db_task.completed_at = datetime.utcnow()
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
        
        # Check if all tasks from this email are completed
        source_email_id = db_task.source_email_id
        incomplete_tasks = db.query(TaskDB).filter(
            TaskDB.source_email_id == source_email_id,
            TaskDB.status != TaskStatus.COMPLETED.value,
            TaskDB.status != TaskStatus.ARCHIVED.value
        ).count()
        
        all_completed = incomplete_tasks == 0
        
        return {
            "task": self._db_to_task(db_task),
            "archive_source_email": all_completed,
            "source_email_id": source_email_id,
            "all_tasks_from_email_completed": all_completed
        }

    def delete_task(self, db: Session, task_id: str) -> bool:
        """Delete a task."""
        
        db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        
        return True

    def _create_task(
        self,
        raw_task: dict,
        email: Email,
        email_priority_score: Optional[int]
    ) -> Task:
        """Create a Task object from raw extraction data."""
        
        # Parse due date if present
        due_date = None
        due_date_type = raw_task.get("due_date_type")
        
        if raw_task.get("due_date"):
            try:
                if isinstance(raw_task["due_date"], str):
                    due_date = datetime.fromisoformat(raw_task["due_date"].replace("Z", "+00:00"))
                else:
                    due_date = raw_task["due_date"]
            except (ValueError, TypeError):
                # Try extracting from original text
                text = raw_task.get("original_text", "")
                extracted = self.deadline_service.extract_due_date(text)
                if extracted:
                    due_date, due_date_type = extracted
        
        # Determine priority from email priority score
        priority_score = email_priority_score or 50
        priority_info = get_priority_level(priority_score)
        priority_label = priority_info["label"]
        
        return Task(
            id=str(uuid.uuid4()),
            title=raw_task.get("title", "Untitled Task")[:100],
            description=raw_task.get("description"),
            due_date=due_date,
            due_date_type=due_date_type,
            priority=priority_label,
            priority_score=priority_score,
            status=TaskStatus.PENDING,
            source_email=SourceEmail(
                id=email.id,
                subject=email.subject,
                sender=email.sender_email
            ),
            original_text=raw_task.get("original_text", ""),
            confidence=raw_task.get("confidence", 0.7),
            created_at=datetime.utcnow()
        )

    def _save_task_to_db(self, db: Session, task: Task):
        """Save a task to the database."""
        
        db_task = TaskDB(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            due_date_type=task.due_date_type,
            priority=task.priority,
            priority_score=task.priority_score,
            status=task.status.value,
            source_email_id=task.source_email.id,
            source_email_subject=task.source_email.subject,
            source_email_sender=task.source_email.sender,
            original_text=task.original_text,
            confidence=task.confidence,
            created_at=task.created_at
        )
        
        db.add(db_task)
        db.commit()

    def _db_to_task(self, db_task: TaskDB) -> Task:
        """Convert database model to Task schema."""
        
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            due_date=db_task.due_date,
            due_date_type=db_task.due_date_type,
            priority=db_task.priority,
            priority_score=db_task.priority_score,
            status=TaskStatus(db_task.status),
            source_email=SourceEmail(
                id=db_task.source_email_id,
                subject=db_task.source_email_subject or "",
                sender=db_task.source_email_sender or ""
            ),
            original_text=db_task.original_text,
            confidence=db_task.confidence,
            created_at=db_task.created_at,
            completed_at=db_task.completed_at
        )
