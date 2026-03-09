"""NLP processing service for keyword extraction and text analysis."""

import logging
import re
from functools import lru_cache

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import settings

logger = logging.getLogger(__name__)

# Ensure NLTK data is available
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


# Common technical skills and keywords for better extraction
TECHNICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "sql", "nosql",
    "react", "angular", "vue", "next.js", "node.js", "express", "django",
    "flask", "fastapi", "spring", "rails", ".net", "laravel",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "ci/cd", "github actions", "gitlab ci",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "cassandra", "sqlite", "oracle",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "rest", "graphql", "grpc", "microservices", "api",
    "git", "linux", "agile", "scrum", "jira", "confluence",
    "html", "css", "sass", "tailwind", "bootstrap",
    "figma", "sketch", "adobe xd",
    "data structures", "algorithms", "system design",
    "unit testing", "integration testing", "tdd", "bdd",
    "oauth", "jwt", "ssl", "encryption", "cybersecurity",
    "hadoop", "spark", "kafka", "airflow", "etl",
    "tableau", "power bi", "looker",
    "ios", "android", "react native", "flutter",
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "mentoring", "presentation", "negotiation",
    "project management", "stakeholder management", "strategic planning",
    "decision making", "conflict resolution", "analytical",
}


@lru_cache(maxsize=1)
def _load_spacy_model():
    """Load and cache the spaCy model."""
    try:
        return spacy.load(settings.SPACY_MODEL)
    except OSError:
        logger.warning(f"spaCy model '{settings.SPACY_MODEL}' not found. Downloading...")
        spacy.cli.download(settings.SPACY_MODEL)
        return spacy.load(settings.SPACY_MODEL)


class NLPProcessor:
    """Handles NLP operations for resume and job description analysis."""

    def __init__(self):
        self.nlp = _load_spacy_model()
        self.stop_words = set(stopwords.words("english"))
        self.tfidf = TfidfVectorizer(
            max_features=200,
            stop_words="english",
            ngram_range=(1, 3),
        )

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)
        # Remove phone numbers
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", text)
        # Remove special characters but keep hyphens, periods, slashes, plus and hash
        text = re.sub(r"[^\w\s\-./+#]", " ", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_keywords(self, text: str) -> list[str]:
        """Extract meaningful keywords from text using spaCy and TF-IDF.

        Combines named entity recognition, noun phrase extraction,
        and TF-IDF scoring for comprehensive keyword extraction.
        """
        cleaned_text = self.preprocess_text(text)
        keywords: set[str] = set()

        # 1. Extract using spaCy NER and noun chunks
        doc = self.nlp(cleaned_text)

        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "GPE", "SKILL", "WORK_OF_ART"):
                keywords.add(ent.text.strip())

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            # Filter out very short or very long chunks
            if 2 <= len(chunk_text) <= 50:
                keywords.add(chunk_text)

        # 2. Extract known technical & soft skills
        text_lower = cleaned_text.lower()
        for skill in TECHNICAL_SKILLS | SOFT_SKILLS:
            if skill in text_lower:
                keywords.add(skill)

        # 3. Extract using TF-IDF on individual tokens
        tokens = word_tokenize(cleaned_text)
        meaningful_tokens = [
            t for t in tokens
            if t not in self.stop_words
            and len(t) > 2
            and not t.isdigit()
        ]

        if meaningful_tokens:
            try:
                tfidf_matrix = self.tfidf.fit_transform([" ".join(meaningful_tokens)])
                feature_names = self.tfidf.get_feature_names_out()
                scores = tfidf_matrix.toarray()[0]

                # Get top keywords by TF-IDF score
                top_indices = scores.argsort()[-30:][::-1]
                for idx in top_indices:
                    if scores[idx] > 0:
                        keywords.add(feature_names[idx])
            except Exception as e:
                logger.warning(f"TF-IDF extraction failed: {e}")

        # Clean and deduplicate
        cleaned_keywords = set()
        for kw in keywords:
            kw_clean = kw.strip().lower()
            if len(kw_clean) > 1 and kw_clean not in self.stop_words:
                cleaned_keywords.add(kw_clean)

        return sorted(cleaned_keywords)

    def extract_technical_skills(self, text: str) -> list[str]:
        """Extract only technical skills from text."""
        text_lower = text.lower()
        return sorted(
            skill for skill in TECHNICAL_SKILLS if skill in text_lower
        )

    def extract_soft_skills(self, text: str) -> list[str]:
        """Extract only soft skills from text."""
        text_lower = text.lower()
        return sorted(
            skill for skill in SOFT_SKILLS if skill in text_lower
        )

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
            section: any(pattern in text_lower for pattern in patterns)
            for section, patterns in section_patterns.items()
        }
