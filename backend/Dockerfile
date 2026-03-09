FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLP models
RUN python -m spacy download en_core_web_sm && \
    python -m nltk.downloader -d /usr/local/nltk_data punkt punkt_tab stopwords averaged_perceptron_tagger wordnet averaged_perceptron_tagger_eng

ENV NLTK_DATA=/usr/local/nltk_data

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
