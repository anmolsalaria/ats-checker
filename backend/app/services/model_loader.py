"""Thread-safe lazy model loader.

All heavy NLP models (spaCy, sentence-transformers, NLTK data)
are loaded on first use — NOT at import time or server startup.
This ensures the FastAPI server starts in < 1 second and avoids
Gunicorn/Render worker-timeout kills.
"""

from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)

_lock = threading.Lock()

# ── Singletons ─────────────────────────────────────────────────────────────
_spacy_model = None
_sentence_model = None
_nltk_ready = False


# ── NLTK data ──────────────────────────────────────────────────────────────

_NLTK_PACKAGES = [
    ("tokenizers", "punkt_tab"),
    ("tokenizers", "punkt"),
    ("corpora", "stopwords"),
    ("taggers", "averaged_perceptron_tagger_eng"),
    ("corpora", "wordnet"),
]


def ensure_nltk() -> None:
    """Download required NLTK data exactly once (thread-safe)."""
    global _nltk_ready
    if _nltk_ready:
        return
    with _lock:
        if _nltk_ready:
            return
        import nltk

        for category, package in _NLTK_PACKAGES:
            try:
                nltk.data.find(f"{category}/{package}")
            except (LookupError, OSError):
                nltk.download(package, quiet=True)
        _nltk_ready = True
        logger.info("NLTK data ready.")


# ── spaCy ──────────────────────────────────────────────────────────────────

def get_spacy_model():
    """Return the cached spaCy model, loading it on first call."""
    global _spacy_model
    if _spacy_model is not None:
        return _spacy_model
    with _lock:
        if _spacy_model is not None:
            return _spacy_model
        import spacy
        from app.config import settings

        model_name = settings.SPACY_MODEL
        logger.info("Loading spaCy model '%s' …", model_name)
        try:
            _spacy_model = spacy.load(model_name)
        except OSError:
            logger.warning("Downloading spaCy model '%s' …", model_name)
            spacy.cli.download(model_name)  # type: ignore[attr-defined]
            _spacy_model = spacy.load(model_name)
        logger.info("spaCy model ready.")
        return _spacy_model


# ── Sentence-transformers ──────────────────────────────────────────────────

def get_sentence_model():
    """Return the cached SentenceTransformer, loading on first call."""
    global _sentence_model
    if _sentence_model is not None:
        return _sentence_model
    with _lock:
        if _sentence_model is not None:
            return _sentence_model
        from sentence_transformers import SentenceTransformer
        from app.config import settings

        model_name = settings.SENTENCE_TRANSFORMER_MODEL
        logger.info("Loading sentence-transformers model '%s' …", model_name)
        _sentence_model = SentenceTransformer(model_name)
        logger.info("Sentence-transformers model ready.")
        return _sentence_model
