"""Configuration settings shared across all features."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Find the root directory (where .env should be)
ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    groq_api_key: Optional[str] = None  # Groq Cloud API key (primary AI provider)
    
    # Database
    database_url: str = "sqlite:///./email_priority.db"
    
    # Environment
    environment: str = "development"
    demo_mode: bool = True
    
    # Scoring weights (can be customized)
    weight_sender_authority: int = 25
    weight_deadline_urgency: int = 25
    weight_emotional_tone: int = 20
    weight_historical_pattern: int = 15
    weight_calendar_conflict: int = 15
    
    # Priority thresholds
    threshold_critical: int = 80
    threshold_high: int = 60
    threshold_medium: int = 40
    threshold_low: int = 20
    
    class Config:
        env_file = str(ROOT_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


# Priority level definitions
PRIORITY_LEVELS = {
    "critical": {"min": 80, "max": 100, "color": "red", "badge": "🔴"},
    "high": {"min": 60, "max": 79, "color": "orange", "badge": "🟠"},
    "medium": {"min": 40, "max": 59, "color": "yellow", "badge": "🟡"},
    "low": {"min": 20, "max": 39, "color": "green", "badge": "🟢"},
    "minimal": {"min": 0, "max": 19, "color": "gray", "badge": "⚪"},
}


def get_priority_level(score: int) -> dict:
    """Get priority level info based on score."""
    for level, info in PRIORITY_LEVELS.items():
        if info["min"] <= score <= info["max"]:
            return {"label": level, **info}
    return {"label": "minimal", **PRIORITY_LEVELS["minimal"]}
