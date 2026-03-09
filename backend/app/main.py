"""AI ATS Resume Analyzer — FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import AnalysisRequest, AnalysisResponse, HealthResponse
from app.services.file_parser import FileParser
from app.services.scorer import ATSScorer
from app.services.suggestions import SuggestionEngine
from app.utils.helpers import setup_logging, truncate_text

logger = logging.getLogger(__name__)

# Pre-load heavy models at startup
scorer: ATSScorer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load NLP models on startup."""
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Endpoints ---------- #


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF or DOCX resume file"),
    job_description: str = Form(..., description="Job description text"),
):
    """Analyze an uploaded resume against a job description.

    - Accepts PDF or DOCX resume files
    - Returns ATS score, keyword analysis, and improvement suggestions
    """
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    # Validate file type
    if resume.content_type not in FileParser.SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {resume.content_type}. "
                f"Please upload a PDF or DOCX file."
            ),
        )

    # Validate file size
    content = await resume.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # Validate job description
    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please provide at least 50 characters.",
        )

    try:
        # Extract resume text
        resume_text = FileParser.extract_text(content, resume.content_type)
        resume_text = truncate_text(resume_text)
        job_description = truncate_text(job_description)

        # Run ATS analysis
        results = scorer.calculate_ats_score(resume_text, job_description)

        # Generate suggestions
        suggestions = SuggestionEngine.generate_suggestions(
            missing_keywords=results["missing_keywords"],
            resume_sections=results["resume_sections"],
            ats_score=results["ats_score"],
            skill_gap=results["skill_gap_analysis"],
        )

        return AnalysisResponse(
            ats_score=results["ats_score"],
            keyword_match_score=results["keyword_match_score"],
            semantic_similarity_score=results["semantic_similarity_score"],
            matched_keywords=results["matched_keywords"],
            missing_keywords=results["missing_keywords"],
            suggestions=suggestions,
            resume_sections=results["resume_sections"],
            skill_gap_analysis=results["skill_gap_analysis"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis. Please try again.",
        )


@app.post("/analyze-text", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_resume_text(request: AnalysisRequest):
    """Analyze resume text directly (without file upload).

    Useful for the Chrome extension or when resume text is already available.
    """
    global scorer
    if scorer is None:
        raise HTTPException(status_code=503, detail="Service is still loading models.")

    try:
        resume_text = truncate_text(request.resume_text)
        job_description = truncate_text(request.job_description)

        results = scorer.calculate_ats_score(resume_text, job_description)

        suggestions = SuggestionEngine.generate_suggestions(
            missing_keywords=results["missing_keywords"],
            resume_sections=results["resume_sections"],
            ats_score=results["ats_score"],
            skill_gap=results["skill_gap_analysis"],
        )

        return AnalysisResponse(
            ats_score=results["ats_score"],
            keyword_match_score=results["keyword_match_score"],
            semantic_similarity_score=results["semantic_similarity_score"],
            matched_keywords=results["matched_keywords"],
            missing_keywords=results["missing_keywords"],
            suggestions=suggestions,
            resume_sections=results["resume_sections"],
            skill_gap_analysis=results["skill_gap_analysis"],
        )

    except Exception as e:
        logger.error(f"Text analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis. Please try again.",
        )
