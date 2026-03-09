"""Tests for the ATS Resume Analyzer API — v3.

Covers:
 - Health endpoint
 - /analyze-text (with JD)
 - /analyze-resume-only (no JD)
 - Keyword extraction quality
 - Bullet-point analysis
 - Role detection
 - ATS grading
 - Validation / error paths
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Fixture: pre-load NLP models once ──────────────────────────────────────

@pytest.fixture(autouse=True, scope="module")
def _load_models():
    """Ensure scorer is initialised before tests run."""
    from app.services.ats_scorer import ATSScorer
    import app.main as main_module

    main_module.scorer = ATSScorer()
    yield


# ── Sample data ────────────────────────────────────────────────────────────

RESUME_TEXT = """
John Doe — Software Engineer

Professional Summary:
Experienced software engineer with 5 years of experience in Python,
JavaScript, React, and REST API development. Strong background in
machine learning and data analysis.

Experience:
Senior Software Engineer at TechCorp (2020 - Present)
- Developed REST APIs using Python and FastAPI, serving 10,000 daily active users
- Built frontend applications with React and TypeScript
- Implemented machine learning models using scikit-learn, improving accuracy by 15%
- Managed PostgreSQL and MongoDB databases
- Improved API response time by 40% through query optimisation

Education:
B.S. Computer Science, University of Technology, 2018

Skills:
Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL,
MongoDB, Docker, Git, Machine Learning, REST APIs
"""

JOB_DESCRIPTION = """
We are looking for a Senior Software Engineer with:
- 5+ years of experience in Python and JavaScript
- Experience with React and modern frontend frameworks
- Background in REST API development
- Machine learning experience is a plus
- Docker and Kubernetes experience
- AWS cloud services knowledge
- Strong communication and teamwork skills
- Experience with CI/CD pipelines
- PostgreSQL or similar databases
"""


# ── Health ─────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


# ── /analyze-text ──────────────────────────────────────────────────────────

def test_analyze_text_returns_all_fields():
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    assert response.status_code == 200
    data = response.json()

    # Core scores
    assert 0 <= data["ats_score"] <= 100
    assert "keyword_match_score" in data
    assert "semantic_similarity_score" in data
    assert "skill_coverage_score" in data
    assert "bullet_quality_score" in data
    assert "structure_score" in data

    # New v3 fields
    assert "ats_grade" in data
    assert data["ats_grade"] in ("A", "B", "C", "D", "F")
    assert "detected_role" in data
    assert isinstance(data["detected_role"], str)
    assert "bullet_analysis" in data
    assert isinstance(data["bullet_analysis"], list)

    # Lists
    assert isinstance(data["matched_keywords"], list)
    assert isinstance(data["missing_keywords"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["skill_gap"], dict)


def test_matched_keywords_are_clean():
    """Matched keywords should not be pure numbers or overly long."""
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    data = response.json()

    for kw in data["matched_keywords"]:
        assert not kw.replace(".", "").replace(",", "").isdigit(), (
            f"Matched keyword should not be a pure number: {kw}"
        )

    for kw in data["missing_keywords"]:
        assert len(kw.split()) <= 3, f"Missing keyword too long: {kw}"


def test_categorised_skill_gap():
    """Verify per-category skill gap in response."""
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    data = response.json()
    gap = data["skill_gap"]

    assert isinstance(gap, dict)
    cats_with_data = [
        c for c, v in gap.items()
        if v.get("required", 0) > 0 or v.get("matched", 0) > 0
    ]
    assert len(cats_with_data) > 0


def test_bullet_analysis_in_response():
    """Bullet analysis items should have required fields."""
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    data = response.json()

    if data["bullet_analysis"]:
        bullet = data["bullet_analysis"][0]
        assert "text" in bullet
        assert "has_action_verb" in bullet
        assert "has_technology" in bullet
        assert "has_metric" in bullet
        assert "score" in bullet
        assert 0 <= bullet["score"] <= 100


# ── /analyze-resume-only ──────────────────────────────────────────────────

def test_analyze_resume_only():
    response = client.post(
        "/analyze-resume-only",
        json={"resume_text": RESUME_TEXT},
    )
    assert response.status_code == 200
    data = response.json()

    assert 0 <= data["resume_strength_score"] <= 100
    assert "strengths" in data
    assert "weaknesses" in data
    assert "suggestions" in data
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["missing_skills"], list)
    assert isinstance(data["categorised_skills"], dict)
    assert "bullet_quality_score" in data
    assert isinstance(data["bullet_analysis"], list)


# ── Keyword Extraction ────────────────────────────────────────────────────

def test_keyword_extraction_filters_junk():
    """Verify dates, numbers, and generic words are NOT extracted."""
    from app.services.keyword_extractor import KeywordExtractor

    extractor = KeywordExtractor()
    text = (
        "23rd march 2024, 6 months experience, double digit million dollars, "
        "work task process the enterprises. Python React Docker AWS."
    )
    keywords = extractor.extract_keywords(text)

    junk = {
        "23rd march", "6 months", "double digit million dollars",
        "work", "task", "process", "the enterprises",
    }
    for j in junk:
        assert j not in keywords, f"Junk keyword found: {j}"

    assert "python" in keywords
    assert "react" in keywords
    assert "docker" in keywords
    assert "aws" in keywords


# ── Bullet Analyzer ───────────────────────────────────────────────────────

def test_bullet_analyzer_detects_action_verbs():
    from app.services.bullet_analyzer import BulletAnalyzer

    analyzer = BulletAnalyzer()
    results = analyzer.analyze_bullets(
        "- Developed a microservice architecture using Python and FastAPI"
    )
    assert len(results) >= 1
    assert results[0]["has_action_verb"] is True
    assert results[0]["action_verb"] == "developed"


def test_bullet_analyzer_detects_metrics():
    from app.services.bullet_analyzer import BulletAnalyzer

    analyzer = BulletAnalyzer()
    results = analyzer.analyze_bullets(
        "- Improved API latency by 35% through caching"
    )
    assert len(results) >= 1
    assert results[0]["has_metric"] is True
    assert any("35%" in m for m in results[0]["metrics"])


def test_bullet_analyzer_detects_technologies():
    from app.services.bullet_analyzer import BulletAnalyzer

    analyzer = BulletAnalyzer()
    results = analyzer.analyze_bullets(
        "- Built a data pipeline using Python, PostgreSQL, and Docker"
    )
    assert len(results) >= 1
    assert results[0]["has_technology"] is True
    assert len(results[0]["technologies"]) >= 1


# ── Role Detector ─────────────────────────────────────────────────────────

def test_role_detector_detects_role():
    from app.services.role_detector import RoleDetector

    detector = RoleDetector()
    role = detector.detect_role(RESUME_TEXT)
    assert isinstance(role, str)
    assert len(role) > 0


# ── ATS Grade ─────────────────────────────────────────────────────────────

def test_ats_grade_mapping():
    from app.services.ats_scorer import get_ats_grade

    assert get_ats_grade(95) == "A"
    assert get_ats_grade(85) == "B"
    assert get_ats_grade(75) == "C"
    assert get_ats_grade(65) == "D"
    assert get_ats_grade(50) == "F"


# ── Validation / Error Paths ──────────────────────────────────────────────

def test_analyze_text_too_short():
    response = client.post(
        "/analyze-text",
        json={"resume_text": "Short.", "job_description": "Also short."},
    )
    assert response.status_code == 422


def test_analyze_unsupported_file_type():
    response = client.post(
        "/analyze",
        files={"resume": ("test.txt", b"Some text content", "text/plain")},
        data={
            "job_description": (
                "A job description that is long enough to pass validation "
                "and be processed correctly."
            )
        },
    )
    assert response.status_code == 400
