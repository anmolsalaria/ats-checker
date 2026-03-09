# Deployment Guide

## Frontend — Vercel

### Prerequisites
- GitHub account
- [Vercel](https://vercel.com) account (free tier works)

### Steps

1. **Push your code to GitHub**.

2. **Import project in Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Select your repository
   - Set **Root Directory** to `frontend`
   - Framework Preset will auto-detect **Next.js**

3. **Set Environment Variables**:
   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://your-backend-name.onrender.com` |

4. **Deploy** — Vercel will build and deploy automatically.

5. **Custom Domain** (optional): Add a custom domain in Vercel project settings.

---

## Backend — Render

### Prerequisites
- GitHub account
- [Render](https://render.com) account (free tier works)

### Steps

1. **Push your code to GitHub**.

2. **Create a new Web Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **New** → **Web Service**
   - Connect your repository
   - Set **Root Directory** to `backend`

3. **Configure the service**:
   | Setting | Value |
   |---------|-------|
   | **Runtime** | Python |
   | **Build Command** | `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -m nltk.downloader punkt stopwords averaged_perceptron_tagger wordnet punkt_tab averaged_perceptron_tagger_eng` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Set Environment Variables**:
   | Variable | Value |
   |----------|-------|
   | `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` |
   | `PYTHON_VERSION` | `3.11.9` |

5. **Deploy** — Render will build and deploy. The first build takes ~5-10 minutes due to model downloads.

### Important Notes

- **Free tier**: Render free instances spin down after 15 minutes of inactivity. The first request after idle takes ~30 seconds.
- **Memory**: The sentence-transformers model requires ~500 MB RAM. Use at least a **512 MB** instance.
- **Persistent disk**: Not required for this application.

---

## Post-Deployment Checklist

- [ ] Backend `/health` endpoint returns `200 OK`
- [ ] Frontend loads and can reach the backend API
- [ ] CORS is configured (backend `ALLOWED_ORIGINS` includes frontend URL)
- [ ] Chrome extension `apiUrl` points to the production backend
- [ ] File uploads work correctly

---

## Chrome Extension — Chrome Web Store (Optional)

1. Zip the `extension/` folder
2. Go to [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
3. Pay the one-time $5 registration fee
4. Upload the ZIP file
5. Fill in the listing details
6. Submit for review

For local use, load the unpacked extension via `chrome://extensions/`.

---

## Environment Variables Reference

### Backend (`.env`)

```env
APP_NAME=AI ATS Resume Analyzer
DEBUG=false
ALLOWED_ORIGINS=["https://your-frontend.vercel.app"]
SPACY_MODEL=en_core_web_sm
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
KEYWORD_WEIGHT=0.6
SEMANTIC_WEIGHT=0.4
MAX_FILE_SIZE_MB=10
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```
