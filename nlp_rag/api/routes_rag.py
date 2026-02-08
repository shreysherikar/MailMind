"""API routes for RAG (semantic search and company memory)."""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from datetime import datetime

from priority_scoring.models.schemas import Email
from nlp_rag.models.schemas import (
    SearchQuery, SearchResponse, CompanyMemoryQuery, CompanyMemoryResponse
)
from nlp_rag.services.rag_service import get_rag_service

router = APIRouter(prefix="/api/v1/rag", tags=["RAG & Search"])


@router.post("/search", response_model=SearchResponse)
async def search_emails(query: SearchQuery):
    """
    Semantic search across email history.
    
    Uses AI embeddings to find emails based on meaning, not just keywords.
    
    Example queries:
    - "Emails about the marketing campaign"
    - "What did John say about deadlines?"
    - "Contract discussions with legal team"
    - "Budget approval emails from last month"
    """
    rag_service = get_rag_service()
    
    try:
        results = rag_service.search_emails(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/ask", response_model=CompanyMemoryResponse)
async def ask_question(query: CompanyMemoryQuery):
    """
    Ask a question about your email history (Company Memory feature).
    
    The AI will search through your emails and provide an answer based on
    the most relevant messages.
    
    Example questions:
    - "What did legal say about the AWS contract?"
    - "When is the project deadline?"
    - "Who approved the budget increase?"
    - "What were the action items from the last meeting?"
    """
    rag_service = get_rag_service()
    
    try:
        response = rag_service.answer_question(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")


@router.post("/index")
async def index_email(email: Email):
    """
    Add an email to the search index.
    
    This makes the email searchable via semantic search and available
    for the company memory feature.
    """
    rag_service = get_rag_service()
    
    try:
        # Parse date if it's a string
        date = email.date if isinstance(email.date, datetime) else datetime.utcnow()
        
        rag_service.index_email(
            email_id=email.id,
            subject=email.subject,
            body=email.body,
            sender=email.sender_email,
            date=date,
            metadata={
                "sender_name": email.sender_name,
                "priority_score": getattr(email, "priority_score", None)
            }
        )
        
        return {
            "status": "indexed",
            "email_id": email.id,
            "message": "Email added to search index"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/index/batch")
async def index_emails_batch(emails: List[Email]):
    """
    Index multiple emails at once for better performance.
    
    Use this when initially loading email history or bulk importing.
    """
    rag_service = get_rag_service()
    
    try:
        # Convert Email objects to dicts
        email_dicts = []
        for email in emails:
            date = email.date if isinstance(email.date, datetime) else datetime.utcnow()
            email_dicts.append({
                "id": email.id,
                "subject": email.subject,
                "body": email.body,
                "sender": email.sender_email,
                "date": date
            })
        
        rag_service.index_emails_batch(email_dicts)
        
        return {
            "status": "indexed",
            "count": len(emails),
            "message": f"Successfully indexed {len(emails)} emails"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch indexing failed: {str(e)}")


@router.delete("/index/{email_id}")
async def delete_from_index(email_id: str):
    """
    Remove an email from the search index.
    
    Use this when an email is deleted or should no longer be searchable.
    """
    rag_service = get_rag_service()
    
    try:
        rag_service.delete_email(email_id)
        return {
            "status": "deleted",
            "email_id": email_id,
            "message": "Email removed from search index"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/stats")
async def get_rag_stats():
    """
    Get statistics about the RAG system.
    
    Returns:
    - Total indexed emails
    - Backend type (chromadb or fallback)
    - Embedding model info
    """
    rag_service = get_rag_service()
    
    try:
        stats = rag_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
