"""Models package for database and Pydantic schemas."""

from .schemas import (
    Email,
    EmailScoreRequest,
    EmailScoreBatchRequest,
    PriorityScore,
    ScoreBreakdown,
    ScoreComponent,
    Task,
    TaskCreate,
    TaskUpdate,
    TaskExtractRequest,
    TaskExtractResponse,
    Contact,
    ContactCreate,
    ContactUpdate,
    AuthorityType,
)
from .database import Base, get_db, engine, ContactDB, ResponseHistoryDB, TaskDB

__all__ = [
    "Email",
    "EmailScoreRequest", 
    "EmailScoreBatchRequest",
    "PriorityScore",
    "ScoreBreakdown",
    "ScoreComponent",
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskExtractRequest",
    "TaskExtractResponse",
    "Contact",
    "ContactCreate",
    "ContactUpdate",
    "AuthorityType",
    "Base",
    "get_db",
    "engine",
    "ContactDB",
    "ResponseHistoryDB",
    "TaskDB",
]
