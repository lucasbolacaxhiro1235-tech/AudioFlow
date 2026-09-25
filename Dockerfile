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

# Using /app as the base directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the 'app' package into /app/app
# This ensures the structure is /app/app/main.py, /app/app/storage/base.py, etc.
COPY backend/app ./app

# Ensure Python can find the 'app' package regardless of where it's called from
ENV PYTHONPATH=/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start uvicorn from /app, importing the package 'app' (located at /app/app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
