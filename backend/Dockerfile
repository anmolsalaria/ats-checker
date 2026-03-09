FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/nltk_data

WORKDIR /app

# System build tools required by blis / thinc / spaCy / numpy.
# libopenblas-dev + liblapack-dev provide BLAS headers that blis needs to compile.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- dependency layer (cached until requirements.txt changes) ---
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Download NLTK corpora at build time so first request is fast.
RUN python -m nltk.downloader -d /usr/local/nltk_data \
    punkt punkt_tab stopwords averaged_perceptron_tagger wordnet averaged_perceptron_tagger_eng || true

# Pre-download sentence-transformers model into image layer.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true

# --- application source ---
COPY . /app

EXPOSE 8000

# Render provides $PORT at runtime; falls back to 8000 locally.
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --log-level info"]
