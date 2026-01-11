"""
Email Priority Scoring & Smart Task Extraction API

A standalone microservice for auto-prioritizing emails and extracting actionable tasks.
Part of the AI-powered email assistant hackathon project.
"""

import sys
from pathlib import Path

# Add the project root to Python path for proper imports
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db
from shared.config import settings
from priority_scoring.api.routes_scoring import router as scoring_router
from priority_scoring.api.routes_contacts import router as contacts_router
from smart_task_extraction.api.routes_tasks import router as tasks_router

# Initialize FastAPI app
app = FastAPI(
    title="Email Priority Scoring & Task Extraction API",
    description="""
## Email Priority Scoring & Smart Task Extraction

This API provides two core features for AI-powered email management:

### 1. Priority Scoring (0-100)
Auto-prioritize emails based on:
- **Sender Authority** (25 pts): VIP, manager, client detection
- **Deadline Urgency** (25 pts): NLP-based deadline extraction
- **Emotional Tone** (20 pts): Sentiment analysis via Gemini AI
- **Historical Patterns** (15 pts): Response time/rate tracking
- **Calendar Conflicts** (15 pts): Meeting/scheduling detection

### 2. Smart Task Extraction
Extract actionable TODO items from emails:
- NLP-powered task detection
- Due date extraction
- Priority inherited from email score
- Auto-archive trigger when tasks complete

### Priority Levels
- 🔴 **Critical** (80-100): Immediate attention required
- 🟠 **High** (60-79): Important, respond soon
- 🟡 **Medium** (40-59): Normal priority
- 🟢 **Low** (20-39): Can wait
- ⚪ **Minimal** (0-19): Low importance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from both features
app.include_router(scoring_router)    # Priority Scoring
app.include_router(contacts_router)   # Contact Management (Priority Scoring)
app.include_router(tasks_router)      # Task Extraction


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")
    print(f"🔑 Gemini API: {'Configured ✓' if settings.gemini_api_key else 'Not configured (using fallback)'}")
    print(f"🌍 Environment: {settings.environment}")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Email Priority Scoring & Task Extraction API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": {
            "priority_scoring": {
                "description": "Auto-prioritize emails (0-100 score)",
                "endpoints": ["/api/v1/emails/score", "/api/v1/contacts"]
            },
            "smart_task_extraction": {
                "description": "Extract actionable TODO items from emails",
                "endpoints": ["/api/v1/tasks"]
            }
        }
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_api": "configured" if settings.gemini_api_key else "not_configured",
        "database": "connected",
        "environment": settings.environment,
        "features": {
            "priority_scoring": "active",
            "smart_task_extraction": "active"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Use localhost for Windows compatibility
        port=8000,
        reload=settings.environment == "development"
    )
