"""Job-role detection service (Feature 7).

Infers the most likely job role from text (typically a JD)
by keyword clustering against a role-keyword map.
"""

from __future__ import annotations

import logging
import re

from app.services.skill_database import ROLE_KEYWORDS

logger = logging.getLogger(__name__)


class RoleDetector:
    """Detects the inferred job role from text content."""

    def detect_role(self, text: str) -> str:
        """Return the most likely role title, or 'Software Engineer' as default."""
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for role, keywords in ROLE_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if len(kw) <= 2:
                    if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                        score += 1
                elif kw in text_lower:
                    score += 1
            scores[role] = score

        if not scores:
            return "Software Engineer"

        best_role = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best_role]

        # Require at least 2 keyword matches to be confident
        if best_score < 2:
            return "Software Engineer"

        return best_role
