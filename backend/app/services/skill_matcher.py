"""Skill matching and gap analysis service (Feature 2 extended).

Compares resume skills against JD skills on a per-category basis.
"""

from __future__ import annotations

import logging
import re

from app.services.skill_database import SKILL_CATEGORIES, get_skill_category
from app.services.keyword_extractor import KeywordExtractor

logger = logging.getLogger(__name__)


class SkillMatcher:
    """Matches resume skills to JD requirements with per-category gap."""

    def __init__(self, extractor: KeywordExtractor):
        self.extractor = extractor

    def calculate_keyword_match(
        self,
        resume_keywords: list[str],
        jd_keywords: list[str],
    ) -> tuple[int, list[str], list[str]]:
        """Score + matched/missing keyword lists.

        Missing keywords are filtered: no dates, numbers, phrases > 2 words.
        """
        resume_set = {kw.lower() for kw in resume_keywords}
        jd_set = {kw.lower() for kw in jd_keywords}

        if not jd_set:
            return 0, [], []

        matched = resume_set & jd_set

        # Substring containment for partial matches
        for jd_kw in jd_set - matched:
            for res_kw in resume_set:
                if jd_kw in res_kw or res_kw in jd_kw:
                    matched.add(jd_kw)
                    break

        missing = jd_set - matched

        # Filter missing keywords — clean only
        clean_missing: set[str] = set()
        for kw in missing:
            if len(kw.split()) > 2:
                continue
            if kw.replace(".", "").replace(",", "").isdigit():
                continue
            clean_missing.add(kw)

        score = int((len(matched) / len(jd_set)) * 100)
        return min(score, 100), sorted(matched), sorted(clean_missing)

    def calculate_skill_coverage(
        self,
        resume_text: str,
        jd_text: str,
    ) -> tuple[int, dict]:
        """Return (coverage_score 0-100, categorised_gap_dict)."""
        res_cats = self.extractor.extract_categorised_skills(resume_text)
        jd_cats = self.extractor.extract_categorised_skills(jd_text)

        gap: dict[str, dict] = {}
        total_required = 0
        total_matched = 0

        for cat in SKILL_CATEGORIES:
            res_set = set(res_cats.get(cat, []))
            jd_set = set(jd_cats.get(cat, []))

            if not jd_set:
                gap[cat] = {
                    "matched": len(res_set & jd_set),
                    "required": 0,
                    "matched_skills": sorted(res_set & jd_set),
                    "missing_skills": [],
                }
                continue

            matched = res_set & jd_set
            missing_skills = jd_set - res_set
            total_required += len(jd_set)
            total_matched += len(matched)
            gap[cat] = {
                "matched": len(matched),
                "required": len(jd_set),
                "matched_skills": sorted(matched),
                "missing_skills": sorted(missing_skills),
            }

        score = int((total_matched / max(total_required, 1)) * 100)
        return min(score, 100), gap
