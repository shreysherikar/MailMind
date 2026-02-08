"""Embedding generation service for semantic search."""

import hashlib
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Using fallback embeddings.")


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is lightweight and fast (384 dimensions).
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                print(f"✅ Loaded embedding model: {model_name} ({self.embedding_dim}D)")
            except Exception as e:
                print(f"Warning: Failed to load embedding model: {e}")
                self.model = None
    
    @property
    def is_available(self) -> bool:
        """Check if embedding model is available."""
        return self.model is not None
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return self._zero_embedding()
        
        if self.is_available:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                print(f"Embedding error: {e}")
                return self._fallback_embedding(text)
        else:
            return self._fallback_embedding(text)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.is_available:
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=len(texts) > 100
                )
                return embeddings.tolist()
            except Exception as e:
                print(f"Batch embedding error: {e}")
                return [self._fallback_embedding(text) for text in texts]
        else:
            return [self._fallback_embedding(text) for text in texts]
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return float((similarity + 1) / 2)
    
    def _zero_embedding(self) -> List[float]:
        """Return a zero embedding vector."""
        return [0.0] * self.embedding_dim
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """
        Generate a simple hash-based embedding as fallback.
        Not semantically meaningful but deterministic.
        """
        # Use hash to generate pseudo-random but deterministic vector
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Convert hash bytes to floats in range [-1, 1]
        embedding = []
        for i in range(0, min(len(text_hash), self.embedding_dim)):
            # Normalize byte value (0-255) to (-1, 1)
            value = (text_hash[i] / 255.0) * 2 - 1
            embedding.append(value)
        
        # Pad with zeros if needed
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]


# Global instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
