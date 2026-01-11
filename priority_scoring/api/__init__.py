"""API routes package."""

from .routes_scoring import router as scoring_router
from .routes_tasks import router as tasks_router
from .routes_contacts import router as contacts_router

__all__ = ["scoring_router", "tasks_router", "contacts_router"]
