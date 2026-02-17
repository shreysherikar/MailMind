"""Vector store for semantic search using ChromaDB."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except Exception as e:
    CHROMADB_AVAILABLE = False
    print(f"Warning: ChromaDB not available ({e}). Using fallback in-memory storage.")

from nlp_rag.services.embedding_service import get_embedding_service


class VectorStore:
    """Vector database for semantic email search."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_service = get_embedding_service()
        
        # Fallback in-memory store
        self.fallback_store: List[Dict[str, Any]] = []
        
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.Client(Settings(
                    persist_directory=persist_directory,
                    anonymized_telemetry=False
                ))
                self.collection = self.client.get_or_create_collection(
                    name="emails",
                    metadata={"description": "Email embeddings for semantic search"}
                )
                print(f"✅ ChromaDB initialized at {persist_directory}")
            except Exception as e:
                print(f"Warning: ChromaDB initialization failed: {e}")
                self.client = None
    
    @property
    def is_available(self) -> bool:
        """Check if vector store is available."""
        return self.client is not None and self.collection is not None
    
    def add_email(
        self,
        email_id: str,
        subject: str,
        body: str,
        sender: str,
        date: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add an email to the vector store.
        
        Args:
            email_id: Unique email identifier
            subject: Email subject
            body: Email body text
            sender: Sender email address
            date: Email date
            metadata: Additional metadata
        """
        # Combine subject and body for embedding
        text = f"{subject}\n\n{body}"
        
        # Generate embedding
        embedding = self.embedding_service.embed_text(text)
        
        # Prepare metadata
        meta = {
            "email_id": email_id,
            "subject": subject,
            "sender": sender,
            "date": date.isoformat(),
            "text_preview": text[:500]
        }
        if metadata:
            meta.update(metadata)
        
        if self.is_available:
            try:
                self.collection.add(
                    ids=[email_id],
                    embeddings=[embedding],
                    metadatas=[meta],
                    documents=[text[:1000]]  # Store preview
                )
            except Exception as e:
                print(f"Error adding to ChromaDB: {e}")
                self._add_to_fallback(email_id, embedding, meta, text)
        else:
            self._add_to_fallback(email_id, embedding, meta, text)
    
    def add_emails_batch(self, emails: List[Dict[str, Any]]):
        """
        Add multiple emails efficiently.
        
        Args:
            emails: List of email dicts with keys: id, subject, body, sender, date
        """
        if not emails:
            return
        
        # Prepare data
        ids = []
        texts = []
        metadatas = []
        
        for email in emails:
            email_id = email["id"]
            subject = email.get("subject", "")
            body = email.get("body", "")
            text = f"{subject}\n\n{body}"
            
            ids.append(email_id)
            texts.append(text)
            metadatas.append({
                "email_id": email_id,
                "subject": subject,
                "sender": email.get("sender", ""),
                "date": email.get("date", datetime.now(timezone.utc)).isoformat(),
                "text_preview": text[:500]
            })
        
        # Generate embeddings in batch
        embeddings = self.embedding_service.embed_batch(texts)
        
        if self.is_available:
            try:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=[t[:1000] for t in texts]
                )
            except Exception as e:
                print(f"Error batch adding to ChromaDB: {e}")
                for i, email_id in enumerate(ids):
                    self._add_to_fallback(email_id, embeddings[i], metadatas[i], texts[i])
        else:
            for i, email_id in enumerate(ids):
                self._add_to_fallback(email_id, embeddings[i], metadatas[i], texts[i])
    
    def search(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for emails.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)
            filters: Optional metadata filters
            
        Returns:
            List of matching emails with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        if self.is_available:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filters
                )
                
                # Format results
                matches = []
                if results and results["ids"] and results["ids"][0]:
                    for i, email_id in enumerate(results["ids"][0]):
                        distance = results["distances"][0][i] if "distances" in results else 0
                        # Convert distance to similarity (assuming cosine distance)
                        similarity = 1 - (distance / 2)  # Normalize to 0-1
                        
                        if similarity >= min_similarity:
                            metadata = results["metadatas"][0][i]
                            matches.append({
                                "email_id": email_id,
                                "similarity": similarity,
                                "subject": metadata.get("subject", ""),
                                "sender": metadata.get("sender", ""),
                                "date": metadata.get("date", ""),
                                "snippet": metadata.get("text_preview", "")
                            })
                
                return matches
            except Exception as e:
                print(f"ChromaDB search error: {e}")
                return self._search_fallback(query_embedding, limit, min_similarity)
        else:
            return self._search_fallback(query_embedding, limit, min_similarity)
    
    def delete_email(self, email_id: str):
        """Delete an email from the vector store."""
        if self.is_available:
            try:
                self.collection.delete(ids=[email_id])
            except Exception as e:
                print(f"Error deleting from ChromaDB: {e}")
        
        # Also remove from fallback
        self.fallback_store = [
            item for item in self.fallback_store
            if item["id"] != email_id
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if self.is_available:
            try:
                count = self.collection.count()
                return {
                    "total_emails": count,
                    "backend": "chromadb",
                    "embedding_model": self.embedding_service.model_name,
                    "embedding_dim": self.embedding_service.embedding_dim
                }
            except Exception:
                pass
        
        return {
            "total_emails": len(self.fallback_store),
            "backend": "fallback",
            "embedding_model": self.embedding_service.model_name,
            "embedding_dim": self.embedding_service.embedding_dim
        }
    
    def _add_to_fallback(
        self,
        email_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        text: str
    ):
        """Add to fallback in-memory store."""
        self.fallback_store.append({
            "id": email_id,
            "embedding": embedding,
            "metadata": metadata,
            "text": text
        })
    
    def _search_fallback(
        self,
        query_embedding: List[float],
        limit: int,
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        """Fallback search using in-memory store."""
        results = []
        
        for item in self.fallback_store:
            similarity = self.embedding_service.compute_similarity(
                query_embedding,
                item["embedding"]
            )
            
            if similarity >= min_similarity:
                results.append({
                    "email_id": item["id"],
                    "similarity": similarity,
                    "subject": item["metadata"].get("subject", ""),
                    "sender": item["metadata"].get("sender", ""),
                    "date": item["metadata"].get("date", ""),
                    "snippet": item["metadata"].get("text_preview", "")
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:limit]


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
