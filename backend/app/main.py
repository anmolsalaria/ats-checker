"""AI ATS Resume Analyzer -- FastAPI Application (v3).

Features:
 1. Strict keyword extraction
 2. Tech skill dictionary
 3. Multi-factor ATS scoring (5 components)
 4. Bullet-point quality analysis
 5. Action-verb detection
 6. Metric detection
 7. Job-role detection
 8. No-JD resume strength mode
 9. ATS grade system
10. LinkedIn job import
11. Frontend animation (handled client-side)
12. Advanced suggestions
13. Performance optimisation
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    AnalysisRequest,
    AnalysisResponse,
    BulletAnalysisItem,
    HealthResponse,
    LinkedInImportRequest,
    ResumeOnlyRequest,
    ResumeStrengthResponse,
)
from app.services.ats_scorer import ATSScorer
from app.services.resume_parser import ResumeParser
from app.services.suggestion_engine import SuggestionEngine
from app.utils.helpers import setup_logging, truncate_text

logger = logging.getLogger(__name__)

# Pre-load heavy models at startup
scorer: ATSScorer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scorer
    setup_logging(settings.DEBUG)
    logger.info("Loading NLP models...")
    scorer = ATSScorer()
    logger.info("Models loaded successfully.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analyze your resume against job descriptions for ATS compatibility.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- helpers ---------- #

def _build_analysis_response(results: dict) -> AnalysisResponse:
    """Map scorer output to the Pydantic response model."""
    resume_text = results.get("_resume_text", "")
    impact_count = (
        scorer.keyword_extractor.count_impact_statements(resume_text)
        if scorer
        else 0
    )

    suggestions = SuggestionEngine.generate_suggestions(
        missing_keywords=results["missing_keywords"],
        resume_sections=results["resume_sections"],
        ats_score=results["ats_score"],
        skill_gap=results.get("skill_gap"),
        impact_count=impact_count,
        bullet_quality_score=results.get("bullet_quality_score", 0),
        detected_role=results.get("detected_role", "Software Engineer"),
    )

    return AnalysisResponse(
        ats_score=results["ats_score"],
        ats_grade=results.get("ats_grade", "F"),
        keyword_match_score=results["keyword_match_score"],
        semantic_similarity_score=results["semantic_similarity_score"],
        skill_coverage_score=results.get("skill_coverage_score", 0),
        bullet_quality_score=results.get("bullet_quality_score", 0),
        structure_score=results.get("structure_score", 0),
        detected_role=results.get("detected_role", "Software Engineer"),
        matched_keywords=results["matched_keywords"],
        missing_keywords=results["missing_keywords"],
        suggestions=suggestions,
        resume_sections=results["resume_sections"],
        skill_gap=results.get("skill_gap", {}),
        bullet_analysis=[
            BulletAnalysisItem(**b) for b in results.get("bullet_analysis", [])
        ],
    )


# ---------- Endpoints ---------- #


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF or DOCX resume file"),
    job_description: str = Form(..., description="Job description text"),
):
    """Analyse an uploaded resume against a job description."""
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    if resume.content_type not in ResumeParser.SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {resume.content_type}. Upload PDF or DOCX.",
        )

    content = await resume.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters.",
        )

    try:
        resume_text = ResumeParser.extract_from_file(content, resume.content_type)
        resume_text = truncate_text(resume_text)
        job_description = truncate_text(job_description)

        results = scorer.calculate_ats_score(resume_text, job_description)
        results["_resume_text"] = resume_text
        return _build_analysis_response(results)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis error. Please try again.")


@app.post("/analyze-text", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_resume_text(request: AnalysisRequest):
    """Analyse resume text directly (no file upload)."""
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    try:
        resume_text = truncate_text(request.resume_text)
        jd = truncate_text(request.job_description)

        results = scorer.calculate_ats_score(resume_text, jd)
        results["_resume_text"] = resume_text
        return _build_analysis_response(results)

    except Exception as e:
        logger.error(f"Text analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis error. Please try again.")


@app.post(
    "/analyze-resume-only",
    response_model=ResumeStrengthResponse,
    tags=["Analysis"],
)
async def analyze_resume_only(request: ResumeOnlyRequest):
    """Analyse a resume without a job description (Feature 8)."""
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    try:
        resume_text = truncate_text(request.resume_text)
        results = scorer.calculate_resume_strength(resume_text)

        impact_count = scorer.keyword_extractor.count_impact_statements(resume_text)
        suggestions = SuggestionEngine.generate_strength_suggestions(
            weaknesses=results["weaknesses"],
            resume_sections=results["resume_sections"],
            impact_count=impact_count,
            bullet_quality_score=results.get("bullet_quality_score", 0),
        )

        return ResumeStrengthResponse(
            resume_strength_score=results["resume_strength_score"],
            tech_coverage_score=results["tech_coverage_score"],
            structure_score=results["structure_score"],
            impact_score=results["impact_score"],
            bullet_quality_score=results.get("bullet_quality_score", 0),
            matched_skills=results["matched_skills"],
            missing_skills=results["missing_skills"],
            categorised_skills=results["categorised_skills"],
            resume_sections=results["resume_sections"],
            strengths=results["strengths"],
            weaknesses=results["weaknesses"],
            suggestions=suggestions,
            bullet_analysis=[
                BulletAnalysisItem(**b) for b in results.get("bullet_analysis", [])
            ],
        )

    except Exception as e:
        logger.error(f"Resume-only analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis error. Please try again.")


@app.post(
    "/analyze-linkedin",
    response_model=AnalysisResponse,
    tags=["Analysis"],
)
async def analyze_linkedin(request: LinkedInImportRequest):
    """Import a JD from a LinkedIn URL and analyse (Feature 10)."""
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    try:
        job_description = ResumeParser.extract_from_linkedin_url(request.linkedin_url)
        resume_text = truncate_text(request.resume_text)
        job_description = truncate_text(job_description)

        results = scorer.calculate_ats_score(resume_text, job_description)
        results["_resume_text"] = resume_text
        return _build_analysis_response(results)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"LinkedIn analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis error. Please try again.")
