# API Documentation

## Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://your-backend.onrender.com`

## Authentication

No authentication is required for the current version. Consider adding API key authentication for production.

---

## Endpoints

### `GET /health`

Check if the service is running and models are loaded.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### `POST /analyze`

Analyze an uploaded resume file against a job description.

**Content-Type**: `multipart/form-data`

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume` | file | Yes | PDF or DOCX file (max 10 MB) |
| `job_description` | string | Yes | Job description text (min 50 chars) |

**Example (cURL)**:
```bash
curl -X POST http://localhost:8000/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=We are looking for a Senior Software Engineer..."
```

**Success Response** (`200 OK`):
```json
{
  "ats_score": 78,
  "keyword_match_score": 72,
  "semantic_similarity_score": 85,
  "matched_keywords": ["python", "react", "rest apis"],
  "missing_keywords": ["docker", "kubernetes", "aws"],
  "suggestions": [
    "Add cloud technologies like AWS, GCP, or Azure"
  ],
  "resume_sections": {
    "experience": true,
    "education": true,
    "skills": true,
    "projects": false,
    "certifications": false,
    "summary": true
  },
  "skill_gap_analysis": {
    "technical": {
      "matched": 8,
      "missing": 3,
      "keywords": ["docker", "kubernetes", "aws"]
    },
    "soft_skills": {
      "matched": 4,
      "missing": 1,
      "keywords": ["negotiation"]
    }
  }
}
```

**Error Responses**:
- `400` — Invalid file type or input too short
- `503` — Models still loading

---

### `POST /analyze-text`

Analyze resume text directly (without file upload). Used by the Chrome extension.

**Content-Type**: `application/json`

**Body**:
```json
{
  "resume_text": "John Doe — Software Engineer...",
  "job_description": "We are looking for..."
}
```

Both fields must be at least 50 characters.

**Response**: Same as `/analyze`.

---

## Error Format

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limits

No rate limits in development. For production, consider adding rate limiting via a reverse proxy (e.g., Nginx) or the `slowapi` library.
