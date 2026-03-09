"""Pydantic models for request/response schemas — v2."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    """Request model for text-based analysis (with JD)."""
    resume_text: str = Field(..., min_length=50, description="Resume text content")
    job_description: str = Field(..., min_length=50, description="Job description text")


class ResumeOnlyRequest(BaseModel):
    """Request model for no-JD resume strength analysis (Feature 6)."""
    resume_text: str = Field(..., min_length=50, description="Resume text content")


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class CategorySkillGap(BaseModel):
    """Per-category skill gap info (Feature 5)."""
    matched: int = 0
    required: int = 0
    matched_skills: list[str] = []
    missing_skills: list[str] = []


class ResumeSections(BaseModel):
    """Detected resume sections."""
    experience: bool = False
    education: bool = False
    skills: bool = False
    projects: bool = False
    certifications: bool = False
    summary: bool = False


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """Response model for resume + JD analysis."""
    ats_score: int = Field(..., ge=0, le=100, description="Overall ATS score")
    keyword_match_score: int = Field(..., ge=0, le=100)
    semantic_similarity_score: int = Field(..., ge=0, le=100)
    skill_coverage_score: int = Field(0, ge=0, le=100)
    structure_score: int = Field(0, ge=0, le=100)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    resume_sections: ResumeSections = Field(default_factory=ResumeSections)
    skill_gap: dict[str, CategorySkillGap] = Field(default_factory=dict)


class ResumeStrengthResponse(BaseModel):
    """Response model for no-JD resume strength analysis (Feature 6)."""
    resume_strength_score: int = Field(..., ge=0, le=100)
    tech_coverage_score: int = Field(0, ge=0, le=100)
    structure_score: int = Field(0, ge=0, le=100)
    impact_score: int = Field(0, ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    categorised_skills: dict[str, list[str]] = Field(default_factory=dict)
    resume_sections: ResumeSections = Field(default_factory=ResumeSections)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
