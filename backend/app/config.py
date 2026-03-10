"""Application configuration."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AI ATS Resume Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3001",
        "http://localhost:3002",
        "https://localhost:3002",
    ]

    # NLP Model
    SPACY_MODEL: str = "en_core_web_sm"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # Scoring weights (v4 — 4-component model, professional ATS style)
    KEYWORD_WEIGHT: float = 0.35
    SEMANTIC_WEIGHT: float = 0.25
    SKILL_COVERAGE_WEIGHT: float = 0.20
    BULLET_QUALITY_WEIGHT: float = 0.20
    STRUCTURE_WEIGHT: float = 0.00  # folded into bullet_quality & skill_coverage

    # File upload
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
