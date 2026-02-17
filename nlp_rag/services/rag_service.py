"""RAG (Retrieval-Augmented Generation) service for company memory."""

from typing import List, Optional
from datetime import datetime, timezone
import time

from nlp_rag.models.schemas import (
    SearchQuery, SearchResponse, SearchResult,
    CompanyMemoryQuery, CompanyMemoryResponse
)
from nlp_rag.services.vector_store_faiss import get_vector_store
from shared.groq_client import get_groq_client


class RAGService:
    """Service for semantic search and question answering over emails."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.vector_store = get_vector_store()
        self.groq = get_groq_client()
    
    def search_emails(self, query: SearchQuery) -> SearchResponse:
        """
        Semantic search across emails.
        
        Args:
            query: Search query with filters
            
        Returns:
            Search results with similarity scores
        """
        start_time = time.time()
        
        # Build filters
        filters = {}
        if query.sender_filter:
            filters["sender"] = query.sender_filter
        
        # Perform vector search
        raw_results = self.vector_store.search(
            query=query.query,
            limit=query.limit,
            min_similarity=query.min_similarity,
            filters=filters if filters else None
        )
        
        # Convert to SearchResult objects
        results = []
        for result in raw_results:
            # Parse date
            try:
                date = datetime.fromisoformat(result["date"])
            except (ValueError, TypeError):
                date = datetime.now(timezone.utc)
            
            results.append(SearchResult(
                email_id=result["email_id"],
                subject=result["subject"],
                sender=result["sender"],
                date=date,
                snippet=result["snippet"],
                similarity_score=result["similarity"]
            ))
        
        # Filter by date if specified
        if query.date_from:
            results = [r for r in results if r.date >= query.date_from]
        if query.date_to:
            results = [r for r in results if r.date <= query.date_to]
        
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResponse(
            query=query.query,
            results=results,
            total_found=len(results),
            search_time_ms=search_time
        )
    
    def answer_question(self, query: CompanyMemoryQuery) -> CompanyMemoryResponse:
        """
        Answer a question using RAG over email history.
        
        This is the "Company Memory" feature - users can ask questions
        like "What did legal say about the AWS contract?" and get answers
        based on past emails.
        
        Args:
            query: Natural language question
            
        Returns:
            AI-generated answer with source emails
        """
        # First, search for relevant emails
        search_query = SearchQuery(
            query=query.question,
            limit=query.limit,
            min_similarity=0.6  # Lower threshold for QA
        )
        
        search_results = self.search_emails(search_query)
        
        if not search_results.results:
            return CompanyMemoryResponse(
                question=query.question,
                answer="I couldn't find any relevant emails to answer this question.",
                sources=[],
                confidence=0.0
            )
        
        # Build context from top results
        context_parts = []
        for i, result in enumerate(search_results.results[:5], 1):
            context_parts.append(
                f"[Email {i}]\n"
                f"From: {result.sender}\n"
                f"Date: {result.date.strftime('%Y-%m-%d')}\n"
                f"Subject: {result.subject}\n"
                f"Content: {result.snippet}\n"
            )
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using Groq or fallback
        if self.groq.is_available:
            answer, confidence = self._generate_answer_with_ai(
                question=query.question,
                context=context
            )
        else:
            answer, confidence = self._generate_answer_fallback(
                question=query.question,
                results=search_results.results
            )
        
        return CompanyMemoryResponse(
            question=query.question,
            answer=answer,
            sources=search_results.results,
            confidence=confidence
        )
    
    def _generate_answer_with_ai(
        self,
        question: str,
        context: str
    ) -> tuple[str, float]:
        """Generate answer using Groq AI."""
        if self.groq.is_available:
            answer = self.groq.answer_question(question, context)
            if answer:
                # Estimate confidence based on answer content
                if "don't have enough information" in answer.lower() or "can't find" in answer.lower():
                    confidence = 0.3
                elif "based on" in answer.lower() or "according to" in answer.lower():
                    confidence = 0.8
                else:
                    confidence = 0.6
                return answer, confidence
        
        return self._generate_answer_fallback(question, [])
    
    def _generate_answer_fallback(
        self,
        question: str,
        results: List[SearchResult]
    ) -> tuple[str, float]:
        """Generate simple answer without AI."""
        if not results:
            return (
                "I found no relevant emails to answer this question.",
                0.0
            )
        
        # Simple answer: list the most relevant emails
        answer_parts = [
            f"I found {len(results)} relevant email(s):",
            ""
        ]
        
        for i, result in enumerate(results[:3], 1):
            answer_parts.append(
                f"{i}. From {result.sender} on {result.date.strftime('%Y-%m-%d')}: "
                f"{result.subject}"
            )
        
        if len(results) > 3:
            answer_parts.append(f"\n...and {len(results) - 3} more emails.")
        
        return "\n".join(answer_parts), 0.5
    
    def index_email(
        self,
        email_id: str,
        subject: str,
        body: str,
        sender: str,
        date: datetime,
        metadata: Optional[dict] = None
    ):
        """
        Add an email to the vector store for searching.
        
        Args:
            email_id: Unique email identifier
            subject: Email subject
            body: Email body text
            sender: Sender email address
            date: Email date
            metadata: Additional metadata
        """
        self.vector_store.add_email(
            email_id=email_id,
            subject=subject,
            body=body,
            sender=sender,
            date=date,
            metadata=metadata
        )
    
    def index_emails_batch(self, emails: List[dict]):
        """
        Index multiple emails efficiently.
        
        Args:
            emails: List of email dicts with keys: id, subject, body, sender, date
        """
        self.vector_store.add_emails_batch(emails)
    
    def delete_email(self, email_id: str):
        """Remove an email from the search index."""
        self.vector_store.delete_email(email_id)
    
    def get_stats(self) -> dict:
        """Get RAG system statistics."""
        return self.vector_store.get_stats()


# Global instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
