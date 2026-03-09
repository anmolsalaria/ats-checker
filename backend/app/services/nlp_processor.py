"""NLP processing service — rewritten for accurate keyword extraction.

Changes from v1:
- Aggressive filtering: drops dates, numbers, generic nouns, short tokens
- Uses curated skill dictionary for detection
- Normalised, deduplicated, lowercase output
- spaCy noun-chunk extraction with strict quality filter
- TF-IDF only retains high-value terms
- Caches the spaCy model for performance (F9)
"""

import logging
import re
from functools import lru_cache

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import settings
from app.services.skill_database import (
    get_all_skills,
    get_skill_category,
    SOFT_SKILLS,
    GENERIC_STOPWORDS,
    SKILL_CATEGORIES,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NLTK bootstrap
# ---------------------------------------------------------------------------
_NLTK_PACKAGES = [
    ("tokenizers", "punkt_tab"),
    ("tokenizers", "punkt"),
    ("corpora", "stopwords"),
    ("taggers", "averaged_perceptron_tagger_eng"),
    ("corpora", "wordnet"),
]

for _category, _package in _NLTK_PACKAGES:
    try:
        nltk.data.find(f"{_category}/{_package}")
    except (LookupError, OSError):
        nltk.download(_package, quiet=True)

# ---------------------------------------------------------------------------
# Precompiled patterns
# ---------------------------------------------------------------------------
_DATE_RE = re.compile(
    r"\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b"
    r"|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*"
    r"|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,4}"
    r"|\b\d{4}\s*[-\u2013]\s*(?:\d{4}|present|current)",
    re.IGNORECASE,
)
_NUMBER_PHRASE_RE = re.compile(
    r"\b\d+[\d,\.]*\s*(?:million|billion|thousand|hundred|percent|%|dollars?"
    r"|months?|years?|weeks?|days?|hours?|minutes?|gb|mb|kb|tb)\b",
    re.IGNORECASE,
)
_PURE_NUMBER_RE = re.compile(r"^\d[\d,\.%\+\-]*$")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_PHONE_RE = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
_SPECIAL_CHAR_RE = re.compile(r"[^\w\s\-./+#]")
_MULTI_SPACE_RE = re.compile(r"\s+")


@lru_cache(maxsize=1)
def _load_spacy_model():
    """Load and cache the spaCy model."""
    try:
        return spacy.load(settings.SPACY_MODEL)
    except OSError:
        logger.warning(f"Downloading spaCy model '{settings.SPACY_MODEL}'...")
        spacy.cli.download(settings.SPACY_MODEL)
        return spacy.load(settings.SPACY_MODEL)


class NLPProcessor:
    """Handles NLP operations for resume and job description analysis."""

    def __init__(self):
        self.nlp = _load_spacy_model()
        self.stop_words = set(stopwords.words("english"))
        self.all_skills = get_all_skills()
        self.tfidf = TfidfVectorizer(
            max_features=200,
            stop_words="english",
            ngram_range=(1, 3),
        )

    # ------------------------------------------------------------------
    # Text cleaning
    # ------------------------------------------------------------------
    def preprocess_text(self, text: str) -> str:
        """Clean and normalise text."""
        text = text.lower()
        text = _URL_RE.sub("", text)
        text = _EMAIL_RE.sub("", text)
        text = _PHONE_RE.sub("", text)
        text = _DATE_RE.sub("", text)
        text = _NUMBER_PHRASE_RE.sub("", text)
        text = _SPECIAL_CHAR_RE.sub(" ", text)
        text = _MULTI_SPACE_RE.sub(" ", text).strip()
        return text

    # ------------------------------------------------------------------
    # Token-level quality gate
    # ------------------------------------------------------------------
    def _is_valid_keyword(self, token: str) -> bool:
        """Return True only for meaningful, non-generic tokens."""
        t = token.strip().lower()
        if len(t) < 2:
            return False
        if _PURE_NUMBER_RE.match(t):
            return False
        if t in self.stop_words:
            return False
        if t in GENERIC_STOPWORDS:
            return False
        if all(c.isdigit() or c in ".,%+-/" for c in t):
            return False
        return True

    # ------------------------------------------------------------------
    # Core keyword extraction (Feature 1 rewrite)
    # ------------------------------------------------------------------
    def extract_keywords(self, text: str) -> list[str]:
        """Extract meaningful, deduplicated keywords.

        Pipeline:
        1. Dictionary skill scan (highest priority)
        2. spaCy noun-chunk extraction (filtered)
        3. TF-IDF top-term extraction (filtered)
        All outputs pass through _is_valid_keyword.
        """
        cleaned = self.preprocess_text(text)
        keywords: set[str] = set()

        # 1. Dictionary skills
        keywords.update(self._scan_skills(cleaned))

        # 2. Soft skills
        keywords.update(self._scan_soft_skills(cleaned))

        # 3. spaCy noun chunks (filtered)
        doc = self.nlp(cleaned)
        for chunk in doc.noun_chunks:
            ct = chunk.text.strip()
            words_in_chunk = ct.split()
            if 1 <= len(words_in_chunk) <= 3 and self._is_valid_keyword(ct):
                if not all(w in GENERIC_STOPWORDS or w in self.stop_words for w in words_in_chunk):
                    keywords.add(ct)

        # 4. TF-IDF top terms (filtered)
        tokens = word_tokenize(cleaned)
        meaningful = [t for t in tokens if self._is_valid_keyword(t)]
        if meaningful:
            try:
                mat = self.tfidf.fit_transform([" ".join(meaningful)])
                names = self.tfidf.get_feature_names_out()
                scores = mat.toarray()[0]
                top_idx = scores.argsort()[-20:][::-1]
                for idx in top_idx:
                    if scores[idx] > 0:
                        term = names[idx]
                        if self._is_valid_keyword(term):
                            keywords.add(term)
            except Exception as e:
                logger.warning(f"TF-IDF extraction failed: {e}")

        # Final clean pass
        cleaned_kws: set[str] = set()
        for kw in keywords:
            kw_clean = kw.strip().lower()
            if self._is_valid_keyword(kw_clean):
                cleaned_kws.add(kw_clean)

        return sorted(cleaned_kws)

    # ------------------------------------------------------------------
    # Dictionary-based skill scanning
    # ------------------------------------------------------------------
    def _scan_skills(self, text_lower: str) -> set[str]:
        """Scan text for known technical skills from the curated DB."""
        found: set[str] = set()
        for skill in self.all_skills:
            if len(skill) <= 2:
                if re.search(rf"\b{re.escape(skill)}\b", text_lower):
                    found.add(skill)
            elif skill in text_lower:
                found.add(skill)
        return found

    def _scan_soft_skills(self, text_lower: str) -> set[str]:
        found: set[str] = set()
        for skill in SOFT_SKILLS:
            if skill in text_lower:
                found.add(skill)
        return found

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------
    def extract_technical_skills(self, text: str) -> list[str]:
        """Extract only known technical skills."""
        return sorted(self._scan_skills(self.preprocess_text(text)))

    def extract_soft_skills(self, text: str) -> list[str]:
        """Extract only soft skills."""
        return sorted(self._scan_soft_skills(self.preprocess_text(text)))

    def extract_categorised_skills(self, text: str) -> dict[str, list[str]]:
        """Return skills found, grouped by category (Feature 5)."""
        cleaned = self.preprocess_text(text)
        cats: dict[str, list[str]] = {cat: [] for cat in SKILL_CATEGORIES}
        for skill in self._scan_skills(cleaned):
            cat = get_skill_category(skill)
            if cat and cat in cats:
                cats[cat].append(skill)
        for cat in cats:
            cats[cat] = sorted(set(cats[cat]))
        return cats

    def detect_resume_sections(self, text: str) -> dict[str, bool]:
        """Detect which standard sections are present in the resume."""
        text_lower = text.lower()
        section_patterns = {
            "experience": [
                "experience", "work history", "employment",
                "professional experience", "work experience",
            ],
            "education": [
                "education", "academic", "university", "degree",
                "bachelor", "master", "phd", "diploma",
            ],
            "skills": [
                "skills", "technical skills", "competencies",
                "technologies", "tools", "proficiencies",
            ],
            "projects": [
                "projects", "personal projects", "portfolio",
                "key projects", "selected projects",
            ],
            "certifications": [
                "certifications", "certificates", "licensed",
                "accreditations", "credentials",
            ],
            "summary": [
                "summary", "objective", "profile", "about me",
                "professional summary", "career objective",
            ],
        }
        return {
            section: any(p in text_lower for p in patterns)
            for section, patterns in section_patterns.items()
        }

    # ------------------------------------------------------------------
    # Impact-statement detection (Feature 8 helper)
    # ------------------------------------------------------------------
    def count_impact_statements(self, text: str) -> int:
        """Count sentences with quantified metrics."""
        patterns = [
            r"\b\d+\s*%",
            r"\$\s*\d+",
            r"\b\d+x\b",
            r"increased|decreased|reduced|improved|saved|generated|grew|boosted",
        ]
        count = 0
        for sent in text.split("."):
            if any(re.search(p, sent, re.IGNORECASE) for p in patterns):
                count += 1
        return count
