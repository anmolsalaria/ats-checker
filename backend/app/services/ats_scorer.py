"""ATS scoring engine (Features 3, 8, 9).

5-component weighted model:
  Keyword Match      -> 35 %
  Semantic Similarity-> 25 %
  Skill Coverage     -> 20 %
  Bullet Quality     -> 10 %
  Resume Structure   -> 10 %

Also provides:
- ATS grade mapping (Feature 9)
- No-JD resume strength analysis (Feature 8)
- Embedding caching (Feature 13)
"""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.services.keyword_extractor import KeywordExtractor
from app.services.skill_matcher import SkillMatcher
from app.services.bullet_analyzer import BulletAnalyzer
from app.services.role_detector import RoleDetector
from app.services.skill_database import (
    SKILL_CATEGORIES,
    get_skill_category,
    SOFT_SKILLS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding cache (Feature 13)
# ---------------------------------------------------------------------------
_embedding_cache: dict[int, np.ndarray] = {}


@lru_cache(maxsize=1)
def _load_sentence_model():
    logger.info(
        f"Loading sentence-transformers model: {settings.SENTENCE_TRANSFORMER_MODEL}"
    )
    return SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)


def _get_embedding(model: SentenceTransformer, text: str) -> np.ndarray:
    key = hash(text)
    if key not in _embedding_cache:
        _embedding_cache[key] = model.encode(
            text, show_progress_bar=False, normalize_embeddings=True
        )
    return _embedding_cache[key]


# ---------------------------------------------------------------------------
# ATS grade mapping (Feature 9)
# ---------------------------------------------------------------------------
def get_ats_grade(score: int) -> str:
    """Map an ATS score to a letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Benchmark for no-JD mode (Feature 8)
# ---------------------------------------------------------------------------
_SE_BENCHMARK_SKILLS: set[str] = {
    "python", "java", "javascript", "typescript", "c++", "sql",
    "react", "node.js", "express", "django", "flask", "spring",
    "postgresql", "mysql", "mongodb", "redis",
    "aws", "docker", "kubernetes", "ci/cd", "linux", "git",
    "rest api", "microservices", "agile", "system design",
    "data structures", "algorithms", "unit testing",
}

_SE_BENCHMARK_SECTIONS: list[str] = [
    "experience", "education", "skills", "projects", "certifications", "summary",
]


class ATSScorer:
    """Calculates ATS compatibility score between a resume and a JD."""

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        self.skill_matcher = SkillMatcher(self.keyword_extractor)
        self.bullet_analyzer = BulletAnalyzer()
        self.role_detector = RoleDetector()
        self.model = _load_sentence_model()

    # ------------------------------------------------------------------
    # Semantic similarity
    # ------------------------------------------------------------------
    def calculate_semantic_similarity(
        self, resume_text: str, jd_text: str
    ) -> int:
        try:
            emb_r = _get_embedding(self.model, resume_text)
            emb_j = _get_embedding(self.model, jd_text)
            sim = cosine_similarity(
                emb_r.reshape(1, -1), emb_j.reshape(1, -1)
            )[0][0]
            return int(max(0, min(100, sim * 100)))
        except Exception as e:
            logger.error(f"Semantic similarity failed: {e}")
            return 0

    # ------------------------------------------------------------------
    # Structure score
    # ------------------------------------------------------------------
    @staticmethod
    def _calculate_structure_score(sections: dict[str, bool]) -> int:
        """Score based on how many standard sections are present."""
        important = ["experience", "education", "skills"]
        nice = ["projects", "certifications", "summary"]

        score = 0
        for s in important:
            if sections.get(s):
                score += 25  # 25 * 3 = 75 max
        for s in nice:
            if sections.get(s):
                score += 8   # ~25 max for 3 nice sections

        return min(score, 100)

    # ------------------------------------------------------------------
    # Full ATS analysis (Feature 3 — 5-component weighted model)
    # ------------------------------------------------------------------
    def calculate_ats_score(
        self, resume_text: str, job_description: str
    ) -> dict:
        """Complete ATS analysis with 5-component weighted scoring."""
        resume_kws = self.keyword_extractor.extract_keywords(resume_text)
        jd_kws = self.keyword_extractor.extract_keywords(job_description)

        keyword_score, matched, missing = self.skill_matcher.calculate_keyword_match(
            resume_kws, jd_kws
        )

        semantic_score = self.calculate_semantic_similarity(
            resume_text, job_description
        )

        skill_coverage_score, skill_gap = self.skill_matcher.calculate_skill_coverage(
            resume_text, job_description
        )

        sections = self.keyword_extractor.detect_resume_sections(resume_text)
        structure_score = self._calculate_structure_score(sections)

        # Bullet quality (Feature 4)
        bullet_quality_score = self.bullet_analyzer.calculate_bullet_quality_score(
            resume_text
        )
        bullet_analysis = self.bullet_analyzer.analyze_bullets(resume_text)

        # Role detection (Feature 7)
        detected_role = self.role_detector.detect_role(job_description)

        # Weighted combination (Feature 3)
        final = int(
            settings.KEYWORD_WEIGHT * keyword_score
            + settings.SEMANTIC_WEIGHT * semantic_score
            + settings.SKILL_COVERAGE_WEIGHT * skill_coverage_score
            + settings.BULLET_QUALITY_WEIGHT * bullet_quality_score
            + settings.STRUCTURE_WEIGHT * structure_score
        )
        final = max(0, min(100, final))

        # ATS grade (Feature 9)
        ats_grade = get_ats_grade(final)

        return {
            "ats_score": final,
            "ats_grade": ats_grade,
            "keyword_match_score": keyword_score,
            "semantic_similarity_score": semantic_score,
            "skill_coverage_score": skill_coverage_score,
            "bullet_quality_score": bullet_quality_score,
            "structure_score": structure_score,
            "detected_role": detected_role,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "resume_sections": sections,
            "skill_gap": skill_gap,
            "bullet_analysis": bullet_analysis,
        }

    # ------------------------------------------------------------------
    # No-JD Resume Strength mode (Feature 8)
    # ------------------------------------------------------------------
    def calculate_resume_strength(self, resume_text: str) -> dict:
        """Analyse resume without a JD using an SE benchmark."""
        sections = self.keyword_extractor.detect_resume_sections(resume_text)

        cleaned = self.keyword_extractor.preprocess_text(resume_text)
        found_skills = self.keyword_extractor._scan_skills(cleaned)
        found_soft = self.keyword_extractor._scan_soft_skills(cleaned)

        benchmark_matched = found_skills & _SE_BENCHMARK_SKILLS
        benchmark_missing = _SE_BENCHMARK_SKILLS - found_skills

        tech_coverage = int(
            (len(benchmark_matched) / max(len(_SE_BENCHMARK_SKILLS), 1)) * 100
        )

        structure_score = self._calculate_structure_score(sections)

        impact_count = self.keyword_extractor.count_impact_statements(resume_text)
        impact_score = min(impact_count * 15, 100)

        bullet_quality_score = self.bullet_analyzer.calculate_bullet_quality_score(
            resume_text
        )
        bullet_analysis = self.bullet_analyzer.analyze_bullets(resume_text)

        cat_skills = self.keyword_extractor.extract_categorised_skills(resume_text)

        # Strengths / weaknesses
        strengths: list[str] = []
        weaknesses: list[str] = []

        if len(found_skills) >= 8:
            strengths.append("Strong technical skill set")
        if sections.get("projects"):
            strengths.append("Includes a Projects section showcasing hands-on work")
        if sections.get("certifications"):
            strengths.append("Has certifications listed")
        if impact_count >= 3:
            strengths.append("Good use of quantified achievements")
        if bullet_quality_score >= 60:
            strengths.append("Strong bullet-point quality with action verbs and metrics")
        if cat_skills.get("cloud"):
            strengths.append("Cloud technologies present")
        if cat_skills.get("devops"):
            strengths.append("DevOps tools present")
        if found_soft:
            strengths.append(
                f"Soft skills mentioned: {', '.join(sorted(found_soft)[:5])}"
            )

        if not cat_skills.get("cloud"):
            weaknesses.append("Missing cloud technologies (AWS, Azure, GCP)")
        if not sections.get("certifications"):
            weaknesses.append("No certifications section")
        if impact_count < 2:
            weaknesses.append("Few quantified achievements — add metrics")
        if not sections.get("summary"):
            weaknesses.append("No professional summary / objective")
        if not sections.get("projects"):
            weaknesses.append("No projects section")
        if len(found_skills) < 5:
            weaknesses.append("Limited technical skills detected")
        if not cat_skills.get("devops"):
            weaknesses.append("Missing DevOps / CI-CD experience")
        if bullet_quality_score < 40:
            weaknesses.append(
                "Bullet points lack action verbs, tech mentions, or metrics"
            )

        # Final strength score (updated weights including bullet quality)
        strength_score = int(
            0.30 * tech_coverage
            + 0.25 * structure_score
            + 0.20 * impact_score
            + 0.15 * bullet_quality_score
            + 0.10 * min(len(found_soft) * 20, 100)
        )
        strength_score = max(0, min(100, strength_score))

        return {
            "resume_strength_score": strength_score,
            "tech_coverage_score": tech_coverage,
            "structure_score": structure_score,
            "impact_score": impact_score,
            "bullet_quality_score": bullet_quality_score,
            "matched_skills": sorted(benchmark_matched),
            "missing_skills": sorted(benchmark_missing),
            "categorised_skills": {k: v for k, v in cat_skills.items() if v},
            "resume_sections": sections,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "bullet_analysis": bullet_analysis,
        }
