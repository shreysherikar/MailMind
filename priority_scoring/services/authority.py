"""Sender authority detection service."""

import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from priority_scoring.models.schemas import Email, ScoreComponent, AuthorityType
from shared.database import ContactDB
from shared.gemini_client import GeminiClient


class AuthorityService:
    """Service for detecting sender authority level."""

    # Authority scores by type
    AUTHORITY_SCORES = {
        AuthorityType.VIP: 25,
        AuthorityType.MANAGER: 22,
        AuthorityType.CLIENT: 20,
        AuthorityType.RECRUITER: 15,
        AuthorityType.COLLEAGUE: 12,
        AuthorityType.EXTERNAL: 8,
        AuthorityType.UNKNOWN: 5,
    }

    # Domain patterns that suggest authority
    DOMAIN_PATTERNS = {
        "client": ["client", "customer", "partner"],
        "recruiter": ["recruit", "talent", "hiring", "hr"],
        "corporate": ["corp", "inc", "llc", "ltd"],
    }

    # Title patterns that suggest authority
    TITLE_PATTERNS = {
        "vip": ["ceo", "cto", "cfo", "coo", "president", "founder", "owner", "director", "vp", "vice president"],
        "manager": ["manager", "lead", "head", "supervisor", "chief"],
    }

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()

    def calculate_score(
        self,
        email: Email,
        db: Optional[Session] = None
    ) -> ScoreComponent:
        """Calculate sender authority score."""
        
        sender_email = email.sender_email.lower()
        sender_name = email.sender_name or ""
        
        # 1. Check database for known contacts
        if db:
            contact = db.query(ContactDB).filter(
                ContactDB.email == sender_email
            ).first()
            
            if contact:
                authority_type = AuthorityType(contact.authority_type)
                base_score = self.AUTHORITY_SCORES.get(authority_type, 5)
                boosted_score = min(25, max(0, base_score + contact.custom_priority_boost))
                
                return ScoreComponent(
                    score=boosted_score,
                    max=25,
                    reason=f"Known {authority_type.value} contact: {contact.name or sender_email}",
                    confidence=1.0
                )
        
        # 2. Check domain patterns
        domain = self._extract_domain(sender_email)
        domain_authority = self._check_domain_patterns(domain)
        
        # 3. Try AI inference from email signature
        signature = self._extract_signature(email.body)
        ai_result = None
        
        if self.gemini.is_available:
            ai_result = self.gemini.infer_sender_authority(
                sender_name, sender_email, signature
            )
        
        # 4. Check for title patterns in name/signature
        title_authority = self._check_title_patterns(sender_name, signature)
        
        # 5. Combine results
        authority_type, confidence, reason = self._combine_signals(
            domain_authority, ai_result, title_authority, sender_name, sender_email
        )
        
        score = self.AUTHORITY_SCORES.get(authority_type, 5)
        
        return ScoreComponent(
            score=score,
            max=25,
            reason=reason,
            confidence=confidence
        )

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if "@" in email:
            return email.split("@")[1].lower()
        return ""

    def _extract_signature(self, body: str) -> str:
        """Extract signature from email body."""
        lines = body.split("\n")
        
        # Look for common signature indicators
        signature_starts = ["--", "regards", "best,", "thanks,", "sincerely", "cheers"]
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for indicator in signature_starts:
                if line_lower.startswith(indicator) or line_lower == indicator:
                    return "\n".join(lines[i:])
        
        # Return last 5 lines as potential signature
        return "\n".join(lines[-5:]) if len(lines) > 5 else ""

    def _check_domain_patterns(self, domain: str) -> Optional[Tuple[AuthorityType, float]]:
        """Check domain against known patterns."""
        domain_lower = domain.lower()
        
        for pattern_type, patterns in self.DOMAIN_PATTERNS.items():
            for pattern in patterns:
                if pattern in domain_lower:
                    if pattern_type == "client":
                        return (AuthorityType.CLIENT, 0.7)
                    elif pattern_type == "recruiter":
                        return (AuthorityType.RECRUITER, 0.7)
        
        # Check for common corporate domains
        if any(ext in domain_lower for ext in [".edu", ".gov", ".org"]):
            return (AuthorityType.EXTERNAL, 0.6)
        
        return None

    def _check_title_patterns(self, name: str, signature: str) -> Optional[Tuple[AuthorityType, float]]:
        """Check for authority indicators in name/signature."""
        text = f"{name} {signature}".lower()
        
        for pattern_type, patterns in self.TITLE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    if pattern_type == "vip":
                        return (AuthorityType.VIP, 0.8)
                    elif pattern_type == "manager":
                        return (AuthorityType.MANAGER, 0.75)
        
        return None

    def _combine_signals(
        self,
        domain_authority: Optional[Tuple[AuthorityType, float]],
        ai_result: Optional[dict],
        title_authority: Optional[Tuple[AuthorityType, float]],
        sender_name: str,
        sender_email: str
    ) -> Tuple[AuthorityType, float, str]:
        """Combine multiple authority signals into final result."""
        
        candidates = []
        
        # Add domain-based result
        if domain_authority:
            candidates.append((domain_authority[0], domain_authority[1], "domain pattern"))
        
        # Add AI result
        if ai_result and ai_result.get("authority_type") != "unknown":
            try:
                ai_type = AuthorityType(ai_result["authority_type"])
                ai_conf = ai_result.get("confidence", 0.7)
                candidates.append((ai_type, ai_conf, "AI inference"))
            except ValueError:
                pass
        
        # Add title-based result
        if title_authority:
            candidates.append((title_authority[0], title_authority[1], "title detection"))
        
        if not candidates:
            return (AuthorityType.UNKNOWN, 0.5, f"Unknown sender: {sender_name or sender_email}")
        
        # Sort by confidence and return highest
        candidates.sort(key=lambda x: (self.AUTHORITY_SCORES.get(x[0], 0), x[1]), reverse=True)
        best = candidates[0]
        
        name_display = sender_name or sender_email
        return (best[0], best[1], f"{best[0].value.title()} detected via {best[2]}: {name_display}")
