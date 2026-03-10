FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/nltk_data

WORKDIR /app

# System build tools required by blis / thinc / spaCy / numpy.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    && rm -rf /var/lib/apt/lists/*

# --- dependency layer (cached until requirements.txt changes) ---
COPY requirements.txt /app/requirements.txt

# Install CPU-only PyTorch FIRST (saves ~1.5 GB vs default CUDA torch)
RUN pip install --upgrade pip setuptools wheel \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /app/requirements.txt

# Download NLTK corpora at build time (small, ~10 MB total).
RUN python -m nltk.downloader -d /usr/local/nltk_data \
    punkt punkt_tab stopwords averaged_perceptron_tagger wordnet averaged_perceptron_tagger_eng || true

# NOTE: We intentionally do NOT pre-load spaCy or sentence-transformers
# models here. They are loaded lazily on first request to keep startup
# instant and avoid Gunicorn worker-timeout kills.

# --- application source ---
COPY . /app

EXPOSE 8000

# Use uvicorn directly (single worker, no gunicorn timeout issues).
# Models load lazily on first request, so startup is < 1 second.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 120 --log-level info"]
