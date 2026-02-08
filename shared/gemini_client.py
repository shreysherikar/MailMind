"""Google Gemini API client wrapper."""

import json
from typing import Optional, Dict, Any

try:
    # Try new package first
    import google.genai as genai
    NEW_GENAI = True
except ImportError:
    try:
        # Fall back to old package
        import google.generativeai as genai
        NEW_GENAI = False
    except ImportError:
        genai = None
        NEW_GENAI = False

from shared.config import settings


class GeminiClient:
    """Wrapper for Google Gemini API interactions."""

    def __init__(self, api_key: str = None):
        """Initialize the Gemini client."""
        self._initialized = False
        try:
            self.api_key = api_key or settings.gemini_api_key
            if not self.api_key:
                print("Warning: No Gemini API key provided. AI features will be disabled.")
                self.model = None
                return

            if genai is None:
                print("Warning: Google Generative AI package not installed. AI features will be disabled.")
                self.model = None
                return

            if NEW_GENAI:
                # New package
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
            else:
                # Old package
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
            
            self._initialized = True
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            self.model = None

    @property
    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return self._initialized and self.model is not None

    def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze emotional tone of email text."""
        if not self.is_available:
            return self._fallback_tone_analysis(text)

        prompt = f"""Analyze the emotional tone of this email and return a JSON object with these fields:
- urgency (0-100): How urgent does the sender seem?
- stress (0-100): Level of stress/pressure in the tone
- anger (0-100): Any signs of frustration or anger
- excitement (0-100): Positive excitement or enthusiasm
- formality (0-100): How formal is the tone (100 = very formal)
- overall_intensity (0-100): Overall emotional intensity

Email text:
\"\"\"
{text[:2000]}
\"\"\"

Return ONLY valid JSON, no other text."""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            if result:
                return result
        except Exception as e:
            print(f"Gemini tone analysis error: {e}")
        
        return self._fallback_tone_analysis(text)

    def extract_tasks(self, subject: str, body: str) -> list:
        """Extract actionable tasks from email content."""
        if not self.is_available:
            return self._fallback_task_extraction(subject, body)

        prompt = f"""Extract actionable tasks from this email. Return a JSON array of tasks.
Each task should have:
- title: Brief task title (max 100 chars)
- description: Detailed description
- due_date: ISO date string if mentioned, null otherwise
- due_date_type: "explicit" (specific date), "relative" (e.g., "next week"), or null
- original_text: The exact text that contains this task
- confidence: 0.0-1.0 how confident you are this is a real task

Only extract ACTIONABLE items that require the recipient to do something.

Subject: {subject}

Body:
\"\"\"
{body[:3000]}
\"\"\"

Return ONLY a valid JSON array, no other text. If no tasks found, return empty array []."""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            if isinstance(result, list):
                return result
        except Exception as e:
            print(f"Gemini task extraction error: {e}")
        
        return self._fallback_task_extraction(subject, body)

    def infer_sender_authority(self, sender_name: str, sender_email: str, signature: str) -> Dict[str, Any]:
        """Infer sender's authority level from email signature and context."""
        if not self.is_available:
            return {"authority_type": "unknown", "confidence": 0.5, "title": None}

        prompt = f"""Analyze this email sender and determine their authority level.
Return a JSON object with:
- authority_type: One of "vip", "manager", "client", "recruiter", "colleague", "external", "unknown"
- confidence: 0.0-1.0
- title: Their job title if detectable, null otherwise
- reasoning: Brief explanation

Sender Name: {sender_name or 'Unknown'}
Sender Email: {sender_email}
Email Signature:
\"\"\"
{signature[:500] if signature else 'No signature'}
\"\"\"

Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            if result:
                return result
        except Exception as e:
            print(f"Gemini authority inference error: {e}")
        
        return {"authority_type": "unknown", "confidence": 0.5, "title": None}

    def _parse_json_response(self, text: str) -> Optional[Any]:
        """Parse JSON from Gemini response, handling markdown code blocks."""
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

    def _fallback_tone_analysis(self, text: str) -> Dict[str, Any]:
        """Rule-based fallback for tone analysis."""
        text_lower = text.lower()
        
        urgency = 0
        stress = 0
        anger = 0
        excitement = 0
        
        # Urgency indicators
        urgent_words = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline', 'today', 'now']
        for word in urgent_words:
            if word in text_lower:
                urgency += 15
        
        # Stress indicators
        stress_words = ['worried', 'concerned', 'issue', 'problem', 'stuck', 'help', 'struggling']
        for word in stress_words:
            if word in text_lower:
                stress += 12
        
        # Anger indicators
        anger_words = ['disappointed', 'unacceptable', 'frustrated', 'complaint', 'terrible', 'worst']
        for word in anger_words:
            if word in text_lower:
                anger += 15
        
        # Excitement indicators
        excitement_words = ['excited', 'great', 'amazing', 'wonderful', 'thrilled', 'congratulations']
        for word in excitement_words:
            if word in text_lower:
                excitement += 15
        
        # Check for exclamation marks and caps
        if text.count('!') > 2:
            urgency += 10
            excitement += 10
        if sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.3:
            urgency += 15
            anger += 10
        
        return {
            "urgency": min(urgency, 100),
            "stress": min(stress, 100),
            "anger": min(anger, 100),
            "excitement": min(excitement, 100),
            "formality": 50,
            "overall_intensity": min((urgency + stress + anger + excitement) // 4, 100)
        }

    def _fallback_task_extraction(self, subject: str, body: str) -> list:
        """Rule-based fallback for task extraction."""
        tasks = []
        text = f"{subject} {body}".lower()
        
        # Common task patterns
        task_patterns = [
            "please review",
            "please send",
            "please update",
            "please complete",
            "please prepare",
            "please schedule",
            "can you",
            "could you",
            "would you",
            "need you to",
            "i need",
            "action required",
            "todo:",
            "task:",
        ]
        
        sentences = body.replace('\n', '. ').split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for pattern in task_patterns:
                if pattern in sentence_lower and len(sentence.strip()) > 10:
                    tasks.append({
                        "title": sentence.strip()[:100],
                        "description": sentence.strip(),
                        "due_date": None,
                        "due_date_type": None,
                        "original_text": sentence.strip(),
                        "confidence": 0.6
                    })
                    break
        
        return tasks[:5]  # Limit to 5 tasks
