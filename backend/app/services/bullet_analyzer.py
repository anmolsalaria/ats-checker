"""Bullet-point quality analysis service (Features 4, 5, 6).

Analyses each resume bullet point for:
- Action verb usage (strong vs weak)
- Technology mention
- Quantified impact / metrics
"""

from __future__ import annotations

import logging
import re

from app.services.skill_database import (
    STRONG_ACTION_VERBS,
    WEAK_VERBS,
    get_all_skills,
)

logger = logging.getLogger(__name__)

# Regex patterns for metric detection (Feature 6)
_METRIC_PATTERNS = [
    re.compile(r"\b\d+\s*%", re.IGNORECASE),
    re.compile(r"\b\d+x\b", re.IGNORECASE),
    re.compile(r"\$\s*[\d,]+\.?\d*", re.IGNORECASE),
    re.compile(r"\b\d{1,3}(?:,\d{3})+\b"),                  # e.g. 100,000
    re.compile(r"\b\d+\.?\d*\s*(?:million|billion|k)\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*(?:users?|customers?|requests?|transactions?)\b", re.IGNORECASE),
    re.compile(r"\b(?:2|3|4|5|6|7|8|9|10)x\s+(?:faster|slower|more|less|improvement)", re.IGNORECASE),
]


class BulletAnalysis:
    """Result of analysing a single bullet point."""

    def __init__(
        self,
        text: str,
        has_action_verb: bool,
        action_verb: str | None,
        is_weak_verb: bool,
        has_technology: bool,
        technologies: list[str],
        has_metric: bool,
        metrics: list[str],
        score: int,
        suggestion: str | None,
    ):
        self.text = text
        self.has_action_verb = has_action_verb
        self.action_verb = action_verb
        self.is_weak_verb = is_weak_verb
        self.has_technology = has_technology
        self.technologies = technologies
        self.has_metric = has_metric
        self.metrics = metrics
        self.score = score  # 0-100
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "has_action_verb": self.has_action_verb,
            "action_verb": self.action_verb,
            "is_weak_verb": self.is_weak_verb,
            "has_technology": self.has_technology,
            "technologies": self.technologies,
            "has_metric": self.has_metric,
            "metrics": self.metrics,
            "score": self.score,
            "suggestion": self.suggestion,
        }


class BulletAnalyzer:
    """Analyses resume bullet points for quality (Feature 4)."""

    # Scoring weights within a bullet
    ACTION_WEIGHT = 0.30
    TECH_WEIGHT = 0.40
    METRIC_WEIGHT = 0.30

    def __init__(self):
        self._all_skills = get_all_skills()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def analyze_bullets(self, resume_text: str) -> list[dict]:
        """Extract and analyse all bullet-like lines from resume text."""
        bullets = self._extract_bullets(resume_text)
        results: list[dict] = []
        for bullet in bullets:
            analysis = self._analyze_single(bullet)
            results.append(analysis.to_dict())
        return results

    def calculate_bullet_quality_score(self, resume_text: str) -> int:
        """Return an overall bullet quality score (0-100)."""
        analyses = self.analyze_bullets(resume_text)
        if not analyses:
            return 0
        total = sum(a["score"] for a in analyses)
        return min(int(total / len(analyses)), 100)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _extract_bullets(self, text: str) -> list[str]:
        """Extract lines that look like resume bullet points."""
        lines = text.split("\n")
        bullets: list[str] = []
        for line in lines:
            stripped = line.strip()
            # Remove common bullet markers
            cleaned = re.sub(r"^[\-\u2022\u2023\u25E6\u2043\*\>]+\s*", "", stripped)
            cleaned = cleaned.strip()
            # Only consider lines that look like achievement statements
            if len(cleaned) >= 20 and len(cleaned.split()) >= 4:
                # Skip section headers and simple labels
                if not cleaned.endswith(":") and not cleaned.isupper():
                    bullets.append(cleaned)
        return bullets[:30]  # Cap at 30 bullets to avoid excessive processing

    def _analyze_single(self, bullet: str) -> BulletAnalysis:
        """Analyse a single bullet point."""
        text_lower = bullet.lower()
        words = text_lower.split()

        # --- Action verb detection (Feature 5) ---
        first_word = words[0].rstrip("ed").rstrip("ing") if words else ""
        first_word_raw = words[0] if words else ""

        has_strong = first_word_raw in STRONG_ACTION_VERBS
        is_weak = first_word_raw in WEAK_VERBS

        # Also check if a strong verb appears anywhere in first 3 words
        action_verb: str | None = None
        for w in words[:3]:
            if w in STRONG_ACTION_VERBS:
                has_strong = True
                action_verb = w
                break
            if w in WEAK_VERBS:
                is_weak = True

        if has_strong and action_verb is None:
            action_verb = first_word_raw

        # --- Technology mention ---
        found_techs: list[str] = []
        for skill in self._all_skills:
            if len(skill) <= 2:
                if re.search(rf"\b{re.escape(skill)}\b", text_lower):
                    found_techs.append(skill)
            elif skill in text_lower:
                found_techs.append(skill)
        has_tech = len(found_techs) > 0

        # --- Metric detection (Feature 6) ---
        found_metrics: list[str] = []
        for pattern in _METRIC_PATTERNS:
            matches = pattern.findall(bullet)
            found_metrics.extend(matches)
        has_metric = len(found_metrics) > 0

        # --- Score ---
        action_score = 100 if has_strong else (30 if not is_weak else 0)
        tech_score = 100 if has_tech else 0
        metric_score = 100 if has_metric else 0

        total_score = int(
            self.ACTION_WEIGHT * action_score
            + self.TECH_WEIGHT * tech_score
            + self.METRIC_WEIGHT * metric_score
        )

        # --- Suggestion ---
        suggestion = self._generate_suggestion(
            has_strong, is_weak, has_tech, has_metric, bullet
        )

        return BulletAnalysis(
            text=bullet,
            has_action_verb=has_strong,
            action_verb=action_verb,
            is_weak_verb=is_weak,
            has_technology=has_tech,
            technologies=sorted(set(found_techs)),
            has_metric=has_metric,
            metrics=found_metrics[:5],
            score=total_score,
            suggestion=suggestion,
        )

    @staticmethod
    def _generate_suggestion(
        has_strong: bool,
        is_weak: bool,
        has_tech: bool,
        has_metric: bool,
        bullet: str,
    ) -> str | None:
        """Generate improvement suggestion for a bullet point."""
        issues: list[str] = []

        if is_weak:
            issues.append(
                "Replace the weak verb with a strong action verb "
                "(e.g., 'Developed', 'Engineered', 'Optimized')"
            )
        elif not has_strong:
            issues.append(
                "Start with a strong action verb "
                "(e.g., 'Built', 'Implemented', 'Designed')"
            )

        if not has_tech:
            issues.append("Mention the specific technologies or tools used")

        if not has_metric:
            issues.append(
                "Add a quantified result "
                "(e.g., 'reducing latency by 40%', 'serving 10K users')"
            )

        if not issues:
            return None

        return ". ".join(issues) + "."
