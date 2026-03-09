"""ATS Scoring engine — v2.

Weighted model (Feature 3):
  Keyword Match      → 40 %
  Semantic Similarity→ 30 %
  Skill Coverage     → 20 %
  Resume Structure   → 10 %

Also provides:
- Categorised skill-gap analysis (Feature 5)
- No-JD resume strength mode   (Feature 6)
- Embedding caching             (Feature 9)
"""

import logging
from functools import lru_cache

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.services.nlp_processor import NLPProcessor
from app.services.skill_database import (
    SKILL_CATEGORIES,
    get_skill_category,
    SOFT_SKILLS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding cache  (Feature 9)
# ---------------------------------------------------------------------------
_embedding_cache: dict[int, np.ndarray] = {}


@lru_cache(maxsize=1)
def _load_sentence_model():
    """Load and cache the sentence-transformers model."""
    logger.info(
        f"Loading sentence-transformers model: {settings.SENTENCE_TRANSFORMER_MODEL}"
    )
    return SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)


def _get_embedding(model: SentenceTransformer, text: str) -> np.ndarray:
    """Return cached embedding or compute a new one."""
    key = hash(text)
    if key not in _embedding_cache:
        _embedding_cache[key] = model.encode(
            text, show_progress_bar=False, normalize_embeddings=True
        )
    return _embedding_cache[key]


# ---------------------------------------------------------------------------
# Benchmark for no-JD mode (Feature 6)
# ---------------------------------------------------------------------------
_SE_BENCHMARK_SKILLS: set[str] = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "sql",
    # Frameworks
    "react", "node.js", "express", "django", "flask", "spring",
    # Databases
    "postgresql", "mysql", "mongodb", "redis",
    # Cloud / DevOps
    "aws", "docker", "kubernetes", "ci/cd", "linux", "git",
    # Concepts
    "rest api", "microservices", "agile", "system design",
    "data structures", "algorithms", "unit testing",
}

_SE_BENCHMARK_SECTIONS: list[str] = [
    "experience", "education", "skills", "projects", "certifications", "summary",
]


class ATSScorer:
    """Calculates ATS compatibility score between a resume and job description."""

    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.model = _load_sentence_model()

    # ------------------------------------------------------------------
    # Keyword match (unchanged interface, cleaner keywords now)
    # ------------------------------------------------------------------
    def calculate_keyword_match(
        self,
        resume_keywords: list[str],
        jd_keywords: list[str],
    ) -> tuple[int, list[str], list[str]]:
        """Score + matched/missing lists.

        Missing keywords are filtered: no dates, numbers, phrases > 3 words (F4).
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

        # Feature 4 — filter missing keywords
        clean_missing: set[str] = set()
        for kw in missing:
            if len(kw.split()) > 3:
                continue
            if kw.replace(".", "").replace(",", "").isdigit():
                continue
            clean_missing.add(kw)

        score = int((len(matched) / len(jd_set)) * 100)
        return min(score, 100), sorted(matched), sorted(clean_missing)

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
    # Skill coverage score  (Feature 3 / 5)
    # ------------------------------------------------------------------
    def _calculate_skill_coverage(
        self, resume_text: str, jd_text: str
    ) -> tuple[int, dict]:
        """Return (coverage_score_0-100, categorised_gap_dict)."""
        res_cats = self.nlp_processor.extract_categorised_skills(resume_text)
        jd_cats = self.nlp_processor.extract_categorised_skills(jd_text)

        gap: dict[str, dict] = {}
        total_required = 0
        total_matched = 0

        for cat in SKILL_CATEGORIES:
            res_set = set(res_cats.get(cat, []))
            jd_set = set(jd_cats.get(cat, []))
            if not jd_set:
                # No requirement in JD for this category — skip
                gap[cat] = {
                    "matched": len(res_set & jd_set),
                    "required": len(jd_set),
                    "matched_skills": sorted(res_set & jd_set),
                    "missing_skills": [],
                }
                continue
            matched = res_set & jd_set
            missing = jd_set - res_set
            total_required += len(jd_set)
            total_matched += len(matched)
            gap[cat] = {
                "matched": len(matched),
                "required": len(jd_set),
                "matched_skills": sorted(matched),
                "missing_skills": sorted(missing),
            }

        score = int((total_matched / max(total_required, 1)) * 100)
        return min(score, 100), gap

    # ------------------------------------------------------------------
    # Resume structure score  (Feature 3)
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
    # Full ATS analysis  (Feature 3 weighted model)
    # ------------------------------------------------------------------
    def calculate_ats_score(
        self, resume_text: str, job_description: str
    ) -> dict:
        """Complete ATS analysis with 4-component weighted scoring."""
        resume_kws = self.nlp_processor.extract_keywords(resume_text)
        jd_kws = self.nlp_processor.extract_keywords(job_description)

        keyword_score, matched, missing = self.calculate_keyword_match(
            resume_kws, jd_kws
        )

        semantic_score = self.calculate_semantic_similarity(
            resume_text, job_description
        )

        skill_coverage_score, skill_gap = self._calculate_skill_coverage(
            resume_text, job_description
        )

        sections = self.nlp_processor.detect_resume_sections(resume_text)
        structure_score = self._calculate_structure_score(sections)

        # Weighted combination (F3)
        final = int(
            0.40 * keyword_score
            + 0.30 * semantic_score
            + 0.20 * skill_coverage_score
            + 0.10 * structure_score
        )
        final = max(0, min(100, final))

        return {
            "ats_score": final,
            "keyword_match_score": keyword_score,
            "semantic_similarity_score": semantic_score,
            "skill_coverage_score": skill_coverage_score,
            "structure_score": structure_score,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "resume_sections": sections,
            "skill_gap": skill_gap,
        }

    # ------------------------------------------------------------------
    # No-JD Resume Strength mode  (Feature 6)
    # ------------------------------------------------------------------
    def calculate_resume_strength(self, resume_text: str) -> dict:
        """Analyse resume without a JD using an SE benchmark."""
        sections = self.nlp_processor.detect_resume_sections(resume_text)

        # Skills found in resume
        found_skills = self.nlp_processor._scan_skills(
            self.nlp_processor.preprocess_text(resume_text)
        )
        found_soft = self.nlp_processor._scan_soft_skills(
            self.nlp_processor.preprocess_text(resume_text)
        )

        # Benchmark comparison
        benchmark_matched = found_skills & _SE_BENCHMARK_SKILLS
        benchmark_missing = _SE_BENCHMARK_SKILLS - found_skills

        tech_coverage = int(
            (len(benchmark_matched) / max(len(_SE_BENCHMARK_SKILLS), 1)) * 100
        )

        structure_score = self._calculate_structure_score(sections)

        impact_count = self.nlp_processor.count_impact_statements(resume_text)
        impact_score = min(impact_count * 15, 100)  # 15 pts per impact statement, max 100

        # Categorised breakdown
        cat_skills = self.nlp_processor.extract_categorised_skills(resume_text)

        # Strengths / weaknesses
        strengths: list[str] = []
        weaknesses: list[str] = []

        if len(found_skills) >= 8:
            strengths.append("Strong technical skill set")
        if sections.get("projects"):
            strengths.append("Includes a Projects section — good for showcasing work")
        if sections.get("certifications"):
            strengths.append("Has certifications listed")
        if impact_count >= 3:
            strengths.append("Good use of quantified achievements")
        if cat_skills.get("cloud"):
            strengths.append("Cloud technologies present")
        if cat_skills.get("devops"):
            strengths.append("DevOps tools present")
        if found_soft:
            strengths.append(f"Soft skills mentioned: {', '.join(sorted(found_soft)[:5])}")

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

        # Final strength score
        strength_score = int(
            0.40 * tech_coverage
            + 0.25 * structure_score
            + 0.20 * impact_score
            + 0.15 * min(len(found_soft) * 20, 100)
        )
        strength_score = max(0, min(100, strength_score))

        return {
            "resume_strength_score": strength_score,
            "tech_coverage_score": tech_coverage,
            "structure_score": structure_score,
            "impact_score": impact_score,
            "matched_skills": sorted(benchmark_matched),
            "missing_skills": sorted(benchmark_missing),
            "categorised_skills": {k: v for k, v in cat_skills.items() if v},
            "resume_sections": sections,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }
