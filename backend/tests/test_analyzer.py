"""Tests for the ATS Resume Analyzer API."""

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


def test_health_check():
    """Test the health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_analyze_text_endpoint():
    """Test the text-based analysis endpoint."""
    resume_text = """
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

    Education:
    B.S. Computer Science, University of Technology, 2018

    Skills:
    Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL,
    MongoDB, Docker, Git, Machine Learning, REST APIs
    """

    job_description = """
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

    response = client.post(
        "/analyze-text",
        json={
            "resume_text": resume_text,
            "job_description": job_description,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "ats_score" in data
    assert 0 <= data["ats_score"] <= 100
    assert "matched_keywords" in data
    assert "missing_keywords" in data
    assert "suggestions" in data
    assert isinstance(data["matched_keywords"], list)
    assert isinstance(data["missing_keywords"], list)
    assert isinstance(data["suggestions"], list)
    assert "keyword_match_score" in data
    assert "semantic_similarity_score" in data


def test_analyze_text_too_short():
    """Test that short inputs are rejected."""
    response = client.post(
        "/analyze-text",
        json={
            "resume_text": "Short.",
            "job_description": "Also short.",
        },
    )
    assert response.status_code == 422


def test_analyze_unsupported_file_type():
    """Test that unsupported file types are rejected."""
    response = client.post(
        "/analyze",
        files={"resume": ("test.txt", b"Some text content", "text/plain")},
        data={"job_description": "A job description that is long enough to pass validation and be processed correctly."},
    )
    assert response.status_code == 400
