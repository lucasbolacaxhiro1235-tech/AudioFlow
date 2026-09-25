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

# We set WORKDIR to / so that 'app' becomes a top-level package in the search path
WORKDIR /

# Install dependencies in a temporary location to keep /app clean
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the 'app' directory from backend to /app
# This results in /app/main.py, /app/storage/base.py, etc.
# But we want the package 'app' to be available, so we copy the folder 'app' into /
COPY backend/app /app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Now the folder /app exists and contains main.py, etc.
# Since the current directory is /, 'import app' finds the folder /app.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
