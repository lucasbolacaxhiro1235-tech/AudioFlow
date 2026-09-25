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

# Use /code to avoid any name collision with the 'app' package
WORKDIR /code

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app package into /code/app
COPY backend/app ./app

# Set the working directory to /code, so 'import app' works perfectly
ENV PYTHONPATH=/code

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /code
USER appuser

EXPOSE 8000

# Start uvicorn. It will find the 'app' package in the current directory /code
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
