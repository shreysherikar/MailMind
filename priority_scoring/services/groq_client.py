"""Groq Cloud API client wrapper for priority scoring services.

Re-exports GroqClient from shared module for use within priority_scoring.
"""

from shared.groq_client import GroqClient, get_groq_client

__all__ = ["GroqClient", "get_groq_client"]
