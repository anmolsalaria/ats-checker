"""Pydantic models for request / response schemas — v3."""

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
    """Request model for no-JD resume strength analysis (Feature 8)."""
    resume_text: str = Field(..., min_length=50, description="Resume text content")


class LinkedInImportRequest(BaseModel):
    """Request model for LinkedIn job import (Feature 10)."""
    linkedin_url: str = Field(..., description="LinkedIn job posting URL")
    resume_text: str = Field(..., min_length=50, description="Resume text content")


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class CategorySkillGap(BaseModel):
    """Per-category skill gap info."""
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


class BulletAnalysisItem(BaseModel):
    """Analysis of a single bullet point (Feature 4)."""
    text: str = ""
    has_action_verb: bool = False
    action_verb: str | None = None
    is_weak_verb: bool = False
    has_technology: bool = False
    technologies: list[str] = []
    has_metric: bool = False
    metrics: list[str] = []
    score: int = Field(0, ge=0, le=100)
    suggestion: str | None = None


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """Response model for resume + JD analysis."""
    ats_score: int = Field(..., ge=0, le=100, description="Overall ATS score")
    ats_grade: str = Field("F", description="Letter grade (A-F)")
    keyword_match_score: int = Field(..., ge=0, le=100)
    semantic_similarity_score: int = Field(..., ge=0, le=100)
    skill_coverage_score: int = Field(0, ge=0, le=100)
    bullet_quality_score: int = Field(0, ge=0, le=100)
    structure_score: int = Field(0, ge=0, le=100)
    detected_role: str = Field("Software Engineer", description="Inferred job role")
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    resume_sections: ResumeSections = Field(default_factory=ResumeSections)
    skill_gap: dict[str, CategorySkillGap] = Field(default_factory=dict)
    bullet_analysis: list[BulletAnalysisItem] = Field(default_factory=list)


class ResumeStrengthResponse(BaseModel):
    """Response model for no-JD resume strength analysis (Feature 8)."""
    resume_strength_score: int = Field(..., ge=0, le=100)
    tech_coverage_score: int = Field(0, ge=0, le=100)
    structure_score: int = Field(0, ge=0, le=100)
    impact_score: int = Field(0, ge=0, le=100)
    bullet_quality_score: int = Field(0, ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    categorised_skills: dict[str, list[str]] = Field(default_factory=dict)
    resume_sections: ResumeSections = Field(default_factory=ResumeSections)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    bullet_analysis: list[BulletAnalysisItem] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
