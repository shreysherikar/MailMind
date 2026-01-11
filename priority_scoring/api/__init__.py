"""Priority Scoring API routes."""

from priority_scoring.api.routes_scoring import router as scoring_router
from priority_scoring.api.routes_contacts import router as contacts_router

__all__ = ["scoring_router", "contacts_router"]
