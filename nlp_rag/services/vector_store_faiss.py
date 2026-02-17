"""Vector store for semantic search using FAISS."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import pickle
import os

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Using fallback in-memory storage.")

from nlp_rag.services.embedding_service import get_embedding_service


class FAISSVectorStore:
    """Vector database for semantic email search using FAISS."""
    
    def __init__(self, persist_directory: str = "./faiss_db"):
        """
        Initialize FAISS vector store.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        self.embedding_service = get_embedding_service()
        self.dimension = self.embedding_service.embedding_dim
        
        # FAISS index
        self.index = None
        self.metadata_store: Dict[str, Dict[str, Any]] = {}
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: Dict[int, str] = {}
        
        # Fallback in-memory store
        self.fallback_store: List[Dict[str, Any]] = []
        
        if FAISS_AVAILABLE:
            try:
                os.makedirs(persist_directory, exist_ok=True)
                self._load_or_create_index()
                print(f"✅ FAISS vector store initialized at {persist_directory}")
            except Exception as e:
                print(f"Warning: FAISS initialization failed: {e}")
                self.index = None
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        index_path = os.path.join(self.persist_directory, "index.faiss")
        metadata_path = os.path.join(self.persist_directory, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata_store = data['metadata']
                    self.id_to_idx = data['id_to_idx']
                    self.idx_to_id = data['idx_to_id']
                print(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"Error loading index: {e}, creating new one")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata_store = {}
        self.id_to_idx = {}
        self.idx_to_id = {}
    
    def _save_index(self):
        """Persist index and metadata to disk."""
        if not FAISS_AVAILABLE or self.index is None:
            return
        
        try:
            index_path = os.path.join(self.persist_directory, "index.faiss")
            metadata_path = os.path.join(self.persist_directory, "metadata.pkl")
            
            faiss.write_index(self.index, index_path)
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata_store,
                    'id_to_idx': self.id_to_idx,
                    'idx_to_id': self.idx_to_id
                }, f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if vector store is available."""
        return FAISS_AVAILABLE and self.index is not None
    
    def add_email(
        self,
        email_id: str,
        subject: str,
        body: str,
        sender: str,
        date: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add an email to the vector store."""
        text = f"{subject}\n\n{body}"
        embedding = self.embedding_service.embed_text(text)
        
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
                # Normalize embedding for cosine similarity
                embedding_np = np.array([embedding], dtype='float32')
                faiss.normalize_L2(embedding_np)
                
                # Add to index
                idx = self.index.ntotal
                self.index.add(embedding_np)
                
                # Store metadata
                self.id_to_idx[email_id] = idx
                self.idx_to_id[idx] = email_id
                self.metadata_store[email_id] = meta
                
                # Persist changes
                self._save_index()
            except Exception as e:
                print(f"Error adding to FAISS: {e}")
                self._add_to_fallback(email_id, embedding, meta, text)
        else:
            self._add_to_fallback(email_id, embedding, meta, text)
    
    def add_emails_batch(self, emails: List[Dict[str, Any]]):
        """Add multiple emails efficiently."""
        if not emails:
            return
        
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
                "date": email.get("date", datetime.utcnow()).isoformat(),
                "text_preview": text[:500]
            })
        
        embeddings = self.embedding_service.embed_batch(texts)
        
        if self.is_available:
            try:
                # Normalize embeddings
                embeddings_np = np.array(embeddings, dtype='float32')
                faiss.normalize_L2(embeddings_np)
                
                # Add to index
                start_idx = self.index.ntotal
                self.index.add(embeddings_np)
                
                # Store metadata
                for i, email_id in enumerate(ids):
                    idx = start_idx + i
                    self.id_to_idx[email_id] = idx
                    self.idx_to_id[idx] = email_id
                    self.metadata_store[email_id] = metadatas[i]
                
                # Persist changes
                self._save_index()
            except Exception as e:
                print(f"Error batch adding to FAISS: {e}")
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
        """Semantic search for emails."""
        query_embedding = self.embedding_service.embed_text(query)
        
        if self.is_available:
            try:
                # Normalize query embedding
                query_np = np.array([query_embedding], dtype='float32')
                faiss.normalize_L2(query_np)
                
                # Search
                similarities, indices = self.index.search(query_np, min(limit * 2, self.index.ntotal))
                
                # Format results
                matches = []
                for i, idx in enumerate(indices[0]):
                    if idx == -1:  # FAISS returns -1 for empty slots
                        continue
                    
                    similarity = float(similarities[0][i])
                    if similarity < min_similarity:
                        continue
                    
                    email_id = self.idx_to_id.get(idx)
                    if not email_id:
                        continue
                    
                    metadata = self.metadata_store.get(email_id, {})
                    
                    # Apply filters if provided
                    if filters:
                        skip = False
                        for key, value in filters.items():
                            if metadata.get(key) != value:
                                skip = True
                                break
                        if skip:
                            continue
                    
                    matches.append({
                        "email_id": email_id,
                        "similarity": similarity,
                        "subject": metadata.get("subject", ""),
                        "sender": metadata.get("sender", ""),
                        "date": metadata.get("date", ""),
                        "snippet": metadata.get("text_preview", "")
                    })
                    
                    if len(matches) >= limit:
                        break
                
                return matches
            except Exception as e:
                print(f"FAISS search error: {e}")
                return self._search_fallback(query_embedding, limit, min_similarity)
        else:
            return self._search_fallback(query_embedding, limit, min_similarity)
    
    def delete_email(self, email_id: str):
        """Delete an email from the vector store."""
        # FAISS doesn't support deletion, so we just remove from metadata
        # The vector remains in the index but won't be returned in searches
        if email_id in self.metadata_store:
            del self.metadata_store[email_id]
        if email_id in self.id_to_idx:
            idx = self.id_to_idx[email_id]
            del self.id_to_idx[email_id]
            if idx in self.idx_to_id:
                del self.idx_to_id[idx]
        
        self._save_index()
        
        # Also remove from fallback
        self.fallback_store = [
            item for item in self.fallback_store
            if item["id"] != email_id
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if self.is_available:
            return {
                "total_emails": len(self.metadata_store),
                "index_vectors": self.index.ntotal,
                "backend": "faiss",
                "embedding_model": self.embedding_service.model_name,
                "embedding_dim": self.embedding_service.embedding_dim
            }
        
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
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]


# Global instance
_vector_store = None


def get_vector_store() -> FAISSVectorStore:
    """Get or create global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore()
    return _vector_store
