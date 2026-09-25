FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Standard project layout
WORKDIR /app

# Copy requirements first
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend folder contents into the current directory (/app)
# This means /app/app/main.py will exist.
COPY backend/ .

# Set PYTHONPATH to /app so that 'import app' finds the /app/app folder
ENV PYTHONPATH=/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run from /app, importing the 'app' package (which is /app/app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
