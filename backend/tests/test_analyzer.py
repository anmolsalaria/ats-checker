"""Tests for the ATS Resume Analyzer API — v2."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def _load_models():
    """Ensure NLP models are loaded before tests run."""
    from app.services.scorer import ATSScorer
    import app.main as main_module

    main_module.scorer = ATSScorer()
    yield


# ---- Health ----

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


# ---- /analyze-text ----

RESUME_TEXT = """
John Doe — Software Engineer

Professional Summary:
Experienced software engineer with 5 years of experience in Python,
JavaScript, React, and REST API development. Strong background in
machine learning and data analysis.

Experience:
Senior Software Engineer at TechCorp (2020 - Present)
- Developed REST APIs using Python and FastAPI
- Built frontend applications with React and TypeScript
- Implemented machine learning models using scikit-learn
- Managed PostgreSQL and MongoDB databases
- Improved API response time by 40%

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


def test_analyze_text_endpoint():
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    assert response.status_code == 200
    data = response.json()

    assert 0 <= data["ats_score"] <= 100
    assert "keyword_match_score" in data
    assert "semantic_similarity_score" in data
    assert "skill_coverage_score" in data
    assert "structure_score" in data
    assert isinstance(data["matched_keywords"], list)
    assert isinstance(data["missing_keywords"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["skill_gap"], dict)

    # Verify matched keywords contain real skills, not junk
    for kw in data["matched_keywords"]:
        assert not kw.replace(".", "").replace(",", "").isdigit(), (
            f"Matched keyword should not be a pure number: {kw}"
        )

    # Missing keywords should be clean
    for kw in data["missing_keywords"]:
        assert len(kw.split()) <= 3, f"Missing keyword too long: {kw}"


def test_keyword_extraction_filters_junk():
    """Verify that dates, numbers, and generic words are NOT extracted."""
    from app.services.nlp_processor import NLPProcessor

    proc = NLPProcessor()
    text = (
        "23rd march 2024, 6 months experience, double digit million dollars, "
        "work task process the enterprises. Python React Docker AWS."
    )
    keywords = proc.extract_keywords(text)

    # Should NOT contain junk
    junk = {"23rd march", "6 months", "double digit million dollars",
            "work", "task", "process", "the enterprises"}
    for j in junk:
        assert j not in keywords, f"Junk keyword found: {j}"

    # Should contain real skills
    assert "python" in keywords
    assert "react" in keywords
    assert "docker" in keywords
    assert "aws" in keywords


def test_categorised_skill_gap():
    """Verify per-category skill gap in response."""
    response = client.post(
        "/analyze-text",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    data = response.json()
    gap = data["skill_gap"]

    # Expect some categories to be present
    assert isinstance(gap, dict)
    # At least languages or frameworks should appear
    cats_with_data = [c for c, v in gap.items() if v.get("required", 0) > 0 or v.get("matched", 0) > 0]
    assert len(cats_with_data) > 0


# ---- /analyze-resume-only (Feature 6) ----

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


# ---- Validation ----

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
        data={"job_description": "A job description that is long enough to pass validation and be processed correctly."},
    )
    assert response.status_code == 400
