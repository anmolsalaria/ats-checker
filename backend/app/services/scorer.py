"""ATS Scoring engine using keyword matching and semantic similarity."""

import logging
from functools import lru_cache

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.services.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_sentence_model():
    """Load and cache the sentence-transformers model."""
    logger.info(f"Loading sentence-transformers model: {settings.SENTENCE_TRANSFORMER_MODEL}")
    return SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)


class ATSScorer:
    """Calculates ATS compatibility score between a resume and job description."""

    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.model = _load_sentence_model()

    def calculate_keyword_match(
        self,
        resume_keywords: list[str],
        jd_keywords: list[str],
    ) -> tuple[int, list[str], list[str]]:
        """Calculate keyword match score.

        Returns:
            Tuple of (score, matched_keywords, missing_keywords)
        """
        resume_set = {kw.lower() for kw in resume_keywords}
        jd_set = {kw.lower() for kw in jd_keywords}

        if not jd_set:
            return 0, [], []

        # Exact matches
        matched = resume_set & jd_set

        # Partial / fuzzy matches (substring containment)
        for jd_kw in jd_set - matched:
            for res_kw in resume_set:
                if jd_kw in res_kw or res_kw in jd_kw:
                    matched.add(jd_kw)
                    break

        missing = jd_set - matched
        score = int((len(matched) / len(jd_set)) * 100)

        return (
            min(score, 100),
            sorted(matched),
            sorted(missing),
        )

    def calculate_semantic_similarity(
        self,
        resume_text: str,
        jd_text: str,
    ) -> int:
        """Calculate semantic similarity using sentence-transformers.

        Uses the all-MiniLM-L6-v2 model to encode both texts and
        compute cosine similarity between their embeddings.
        """
        try:
            # Encode both texts
            embeddings = self.model.encode(
                [resume_text, jd_text],
                show_progress_bar=False,
                normalize_embeddings=True,
            )

            # Compute cosine similarity
            sim = cosine_similarity(
                embeddings[0].reshape(1, -1),
                embeddings[1].reshape(1, -1),
            )[0][0]

            # Scale to 0-100 range
            # Cosine similarity ranges from -1 to 1, but for text it's usually 0-1
            score = int(max(0, min(100, sim * 100)))
            return score

        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0

    def calculate_ats_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> dict:
        """Calculate the complete ATS analysis.

        Algorithm:
            1. Extract keywords from both texts
            2. Calculate keyword match score (60% weight)
            3. Calculate semantic similarity score (40% weight)
            4. Compute weighted final score
            5. Generate skill gap analysis

        Returns:
            Complete analysis result dictionary.
        """
        # Extract keywords
        resume_keywords = self.nlp_processor.extract_keywords(resume_text)
        jd_keywords = self.nlp_processor.extract_keywords(job_description)

        # Keyword matching
        keyword_score, matched, missing = self.calculate_keyword_match(
            resume_keywords, jd_keywords
        )

        # Semantic similarity
        semantic_score = self.calculate_semantic_similarity(
            resume_text, job_description
        )

        # Weighted final score
        final_score = int(
            settings.KEYWORD_WEIGHT * keyword_score
            + settings.SEMANTIC_WEIGHT * semantic_score
        )
        final_score = max(0, min(100, final_score))

        # Skill gap analysis
        resume_tech = set(self.nlp_processor.extract_technical_skills(resume_text))
        jd_tech = set(self.nlp_processor.extract_technical_skills(job_description))
        resume_soft = set(self.nlp_processor.extract_soft_skills(resume_text))
        jd_soft = set(self.nlp_processor.extract_soft_skills(job_description))

        tech_matched = resume_tech & jd_tech
        tech_missing = jd_tech - resume_tech
        soft_matched = resume_soft & jd_soft
        soft_missing = jd_soft - resume_soft

        # Resume sections
        sections = self.nlp_processor.detect_resume_sections(resume_text)

        return {
            "ats_score": final_score,
            "keyword_match_score": keyword_score,
            "semantic_similarity_score": semantic_score,
            "matched_keywords": sorted(set(matched) | tech_matched | soft_matched),
            "missing_keywords": sorted(set(missing) | tech_missing | soft_missing),
            "resume_sections": sections,
            "skill_gap_analysis": {
                "technical": {
                    "matched": len(tech_matched),
                    "missing": len(tech_missing),
                    "keywords": sorted(tech_missing),
                },
                "soft_skills": {
                    "matched": len(soft_matched),
                    "missing": len(soft_missing),
                    "keywords": sorted(soft_missing),
                },
            },
        }
