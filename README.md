<div align="center">

# AI ATS Resume Analyzer

**Optimize your resume for Applicant Tracking Systems with AI-powered NLP analysis.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab.svg?logo=python&logoColor=white)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-000000.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178c6.svg?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06b6d4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Manifest_V3-4285f4.svg?logo=googlechrome&logoColor=white)](#chrome-extension-setup)

[Features](#-features) · [Demo](#-screenshots) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Deployment](#-deployment) · [Contributing](#-contributing)

</div>

---

## About

AI ATS Resume Analyzer is a full-stack application that helps job seekers maximize their chances of passing Applicant Tracking Systems. Upload your resume, paste a job description, and get instant AI-powered feedback.

### What it does

1. **Upload a resume** — supports PDF and DOCX formats
2. **Paste or extract a job description** — manually or automatically via Chrome extension
3. **Get an ATS compatibility score** — powered by NLP keyword matching and semantic similarity
4. **Receive actionable feedback** — matched/missing keywords, skill gap analysis, and improvement suggestions

---

## Features

<table>
<tr>
<td width="50%">

### Web Application
- Drag-and-drop resume upload (PDF & DOCX)
- Job description text input
- ATS compatibility score (0–100%)
- Keyword extraction and matching
- Missing keyword detection
- Resume improvement suggestions
- Semantic similarity scoring
- Skill gap analysis
- Resume section detection
- Clean, modern, responsive UI

</td>
<td width="50%">

### Chrome Extension
- Detects job descriptions on **LinkedIn**, **Indeed**, **Glassdoor**, **Monster**
- One-click job description extraction
- Sends data to backend API
- Displays ATS score in extension popup
- Configurable API endpoint

</td>
</tr>
</table>

### NLP Pipeline
- **spaCy** — Named Entity Recognition and noun chunk extraction
- **NLTK** — Tokenization and text preprocessing
- **scikit-learn** — TF-IDF vectorization for keyword extraction
- **sentence-transformers** — Semantic similarity using `all-MiniLM-L6-v2` embeddings

---

## Tech Stack

| Layer | Technologies |
|:------|:------------|
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS |
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **NLP / ML** | spaCy, NLTK, scikit-learn, sentence-transformers |
| **File Processing** | PyPDF2, python-docx |
| **Extension** | Chrome Manifest V3, JavaScript |
| **Deployment** | Vercel (frontend), Render (backend), Docker |

---

## Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│   Next.js App   │──────▶│  FastAPI Backend │◀──────│ Chrome Extension│
│   (Vercel)      │  API  │  (Render)        │  API  │ (Browser)       │
│                 │       │                 │       │                 │
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                          ┌────────┴────────┐
                          │  NLP Pipeline   │
                          │                 │
                          │  • spaCy NER    │
                          │  • TF-IDF       │
                          │  • Sentence     │
                          │    Transformers │
                          └─────────────────┘
```

---

## Project Structure

```
ATS_Checker/
│
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                 # Application entry point & API routes
│   │   ├── config.py               # Settings & environment config
│   │   ├── models.py               # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── file_parser.py      # PDF & DOCX text extraction
│   │   │   ├── nlp_processor.py    # NLP keyword extraction engine
│   │   │   ├── scorer.py           # ATS scoring algorithm
│   │   │   └── suggestions.py      # Improvement suggestion generator
│   │   └── utils/
│   │       └── helpers.py          # Utility functions
│   ├── tests/
│   │   └── test_analyzer.py        # API & analysis tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml                 # Render deployment config
│
├── frontend/                       # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Home page (upload & input)
│   │   │   ├── globals.css         # Global styles
│   │   │   └── results/
│   │   │       └── page.tsx        # Results dashboard
│   │   ├── components/
│   │   │   ├── FileUpload.tsx      # Drag-and-drop file uploader
│   │   │   ├── JobDescriptionInput.tsx
│   │   │   ├── ScoreDisplay.tsx    # Circular progress score
│   │   │   ├── KeywordList.tsx     # Keyword chips (matched/missing)
│   │   │   ├── Suggestions.tsx     # Improvement suggestions list
│   │   │   └── Header.tsx          # Navigation header
│   │   ├── lib/
│   │   │   └── api.ts              # API client
│   │   └── types/
│   │       └── index.ts            # TypeScript interfaces
│   ├── tailwind.config.ts
│   ├── package.json
│   └── tsconfig.json
│
├── extension/                      # Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── popup.html & popup.js       # Extension popup UI
│   ├── content.js                  # Job description extractor
│   ├── background.js               # Service worker
│   ├── styles.css
│   └── icons/
│
├── docs/                           # Documentation
│   ├── API.md                      # API reference
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── CONTRIBUTING.md             # Contribution guidelines
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Quick Start

### Prerequisites

| Requirement | Version |
|:-----------|:--------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| Google Chrome | Latest (for extension) |

### 1. Clone the Repository

```bash
git clone https://github.com/anmolsingh/ATS_Checker.git
cd ATS_Checker
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "
import ssl, nltk
try: ssl._create_default_https_context = ssl._create_unverified_context
except: pass
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
"

# Start the server
uvicorn app.main:app --reload --port 8000
```

> Backend: **http://localhost:8000**
> Interactive API docs: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

> Frontend: **http://localhost:3000**

### 4. Chrome Extension Setup

1. Open Chrome → navigate to `chrome://extensions/`
2. Enable **Developer Mode** (toggle, top right)
3. Click **Load Unpacked**
4. Select the `extension/` folder from this project
5. The ATS Analyzer icon will appear in your toolbar

---

## API Reference

### `POST /analyze` — Analyze resume file

Upload a resume file and compare against a job description.

**Request** `multipart/form-data`:

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `resume` | File | ✅ | PDF or DOCX resume (max 10 MB) |
| `job_description` | String | ✅ | Job description text (min 50 chars) |

**Response** `200 OK`:

```json
{
  "ats_score": 78,
  "keyword_match_score": 72,
  "semantic_similarity_score": 85,
  "matched_keywords": ["python", "react", "rest apis", "machine learning"],
  "missing_keywords": ["docker", "kubernetes", "aws"],
  "suggestions": [
    "Add cloud technologies like AWS, GCP, or Azure",
    "Include measurable achievements with metrics",
    "Strengthen your skills section with missing keywords"
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
    "technical": { "matched": 8, "missing": 3, "keywords": ["docker", "kubernetes", "aws"] },
    "soft_skills": { "matched": 4, "missing": 1, "keywords": ["negotiation"] }
  }
}
```

### `POST /analyze-text` — Analyze resume text

Same response format. Send JSON body with `resume_text` and `job_description` strings. Used by the Chrome extension.

### `GET /health` — Health check

Returns `{ "status": "healthy", "version": "1.0.0" }`

> See [docs/API.md](docs/API.md) for complete API documentation.

---

## Scoring Algorithm

The ATS score is calculated using a weighted combination of two metrics:

$$\text{ATS Score} = 0.6 \times \text{Keyword Match} + 0.4 \times \text{Semantic Similarity}$$

| Component | Weight | Method |
|:----------|:-------|:-------|
| **Keyword Match** | 60% | TF-IDF keyword extraction → Jaccard similarity on keyword sets |
| **Semantic Similarity** | 40% | Sentence-transformers `all-MiniLM-L6-v2` embeddings → cosine similarity |

**Example Output:**

```
ATS Score: 78%

✅ Matched Skills:  Python, React, REST APIs, Machine Learning
❌ Missing Skills:  Docker, Kubernetes, AWS

💡 Suggestions:
   • Add cloud technologies like AWS, GCP, or Azure
   • Include measurable achievements with metrics
   • Add a dedicated Skills section
```

---

## Screenshots

> *Add screenshots after running the application.*

| Home Page | Results Dashboard |
|:---------:|:-----------------:|
| ![Home](docs/screenshots/home.png) | ![Results](docs/screenshots/results.png) |

| Chrome Extension |
|:----------------:|
| ![Extension](docs/screenshots/extension.png) |

---

## Deployment

### Frontend → Vercel

1. Push code to GitHub
2. Import project in [Vercel](https://vercel.com) → set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
4. Deploy

### Backend → Render

1. Create a new **Web Service** on [Render](https://render.com) → set root directory to `backend`
2. **Build command:**
   ```
   pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -m nltk.downloader punkt punkt_tab stopwords averaged_perceptron_tagger wordnet averaged_perceptron_tagger_eng
   ```
3. **Start command:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Set env var `ALLOWED_ORIGINS` to your Vercel frontend URL

> See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions including Docker setup.

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

```
tests/test_analyzer.py::test_health_check              PASSED
tests/test_analyzer.py::test_analyze_text_endpoint      PASSED
tests/test_analyzer.py::test_analyze_text_too_short     PASSED
tests/test_analyzer.py::test_analyze_unsupported_file   PASSED

======================== 4 passed ========================
```

---

## Roadmap

- [ ] Multi-language resume support
- [ ] Resume template generator
- [ ] Batch resume analysis
- [ ] Job description database & history
- [ ] User accounts with saved analyses
- [ ] PDF export of analysis reports
- [ ] Integration with more job sites
- [ ] AI-powered resume rewriting suggestions
- [ ] ATS format checker (fonts, tables, images)
- [ ] LinkedIn profile import

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for job seekers everywhere**

⭐ Star this repo if you found it helpful!

</div>
