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

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy EVERYTHING from backend to /app
COPY backend/ .

# The app code is now in /app/app
# We set PYTHONPATH to /app so that 'import app' resolves to /app/app
ENV PYTHONPATH=/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start uvicorn. We call the module 'app.main' 
# which Python finds in /app/app/main.py thanks to PYTHONPATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
