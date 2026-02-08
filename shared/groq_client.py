"""Groq Cloud API client wrapper."""

import json
from typing import Optional, Dict, Any
import requests

from shared.config import settings


class GroqClient:
    """Wrapper for Groq Cloud API interactions."""
    
    def __init__(self, api_key: str = None):
        """Initialize the Groq client."""
        self._initialized = False
        self.api_key = api_key or getattr(settings, 'groq_api_key', None)
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            print("Warning: No Groq API key provided. AI features will use fallback.")
            return
        
        self._initialized = True
        print("✅ Groq API initialized")
    
    @property
    def is_available(self) -> bool:
        """Check if Groq API is available."""
        return self._initialized and self.api_key is not None
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Generate text using Groq."""
        if not self.is_available:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    def summarize_email(self, subject: str, body: str) -> Dict[str, Any]:
        """Generate email summary."""
        if not self.is_available:
            return None
        
        prompt = f"""Analyze this email and provide a structured summary in JSON format:

{{
  "short_summary": "One-line summary (max 100 chars)",
  "detailed_summary": "2-3 sentence detailed summary",
  "key_points": ["bullet point 1", "bullet point 2", ...],
  "action_items": ["action 1", "action 2", ...],
  "entities": [
    {{"text": "entity name", "type": "person|organization|date|location|money|project|product", "confidence": 0.9}}
  ],
  "intent": "request|question|information|complaint|meeting|followup|acknowledgment|unknown",
  "confidence": 0.85
}}

Subject: {subject}

Body:
\"\"\"
{body[:4000]}
\"\"\"

Return ONLY valid JSON."""
        
        try:
            response = self.generate_text(prompt, max_tokens=1500)
            if response:
                return self._parse_json_response(response)
        except Exception as e:
            print(f"Groq summarization error: {e}")
        
        return None
    
    def answer_question(self, question: str, context: str) -> Optional[str]:
        """Answer a question based on context (for RAG)."""
        if not self.is_available:
            return None
        
        prompt = f"""You are an AI assistant helping users find information from their email history.

Based on the email excerpts below, answer the user's question. Be concise and cite which email(s) you're referencing.

If the emails don't contain enough information to answer the question, say so honestly.

Question: {question}

Email Context:
{context}

Provide a clear, helpful answer based on the emails above. Start your answer directly without preamble."""
        
        try:
            return self.generate_text(prompt, max_tokens=500)
        except Exception as e:
            print(f"Groq question answering error: {e}")
            return None
    
    def _parse_json_response(self, text: str) -> Optional[Any]:
        """Parse JSON from Groq response."""
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start_idx = text.find('{')
            if start_idx == -1:
                start_idx = text.find('[')
            if start_idx != -1:
                try:
                    return json.loads(text[start_idx:])
                except Exception:
                    pass
            return None


# Global instance
_groq_client = None


def get_groq_client() -> GroqClient:
    """Get or create global Groq client instance."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
