"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request model for text-based analysis."""

    resume_text: str = Field(..., min_length=50, description="Resume text content")
    job_description: str = Field(
        ..., min_length=50, description="Job description text"
    )


class SkillGap(BaseModel):
    """Skill gap breakdown."""

    matched: int
    missing: int
    keywords: list[str] = []


class SkillGapAnalysis(BaseModel):
    """Skill gap analysis result."""

    technical: SkillGap
    soft_skills: SkillGap


class ResumeSections(BaseModel):
    """Detected resume sections."""

    experience: bool = False
    education: bool = False
    skills: bool = False
    projects: bool = False
    certifications: bool = False
    summary: bool = False


class AnalysisResponse(BaseModel):
    """Response model for resume analysis."""

    ats_score: int = Field(..., ge=0, le=100, description="Overall ATS score (0-100)")
    keyword_match_score: int = Field(
        ..., ge=0, le=100, description="Keyword match percentage"
    )
    semantic_similarity_score: int = Field(
        ..., ge=0, le=100, description="Semantic similarity percentage"
    )
    matched_keywords: list[str] = Field(
        default_factory=list, description="Keywords found in resume"
    )
    missing_keywords: list[str] = Field(
        default_factory=list, description="Keywords missing from resume"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )
    resume_sections: ResumeSections = Field(
        default_factory=ResumeSections, description="Detected resume sections"
    )
    skill_gap_analysis: SkillGapAnalysis | None = Field(
        None, description="Skill gap breakdown"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
