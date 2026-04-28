# NYX Backend — Production Dockerfile
# Multi-stage build for smaller image size

# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user for security
RUN groupadd -r nyx && useradd -r -g nyx nyx

# Copy installed packages from builder
COPY --from=builder /root/.local /home/nyx/.local
ENV PATH=/home/nyx/.local/bin:$PATH

# Copy application code
COPY backend/ ./backend/
COPY docs/ ./docs/

# If you have a built frontend to serve statically, uncomment:
# COPY frontend/build/ ./frontend/

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Switch to non-root user
RUN chown -R nyx:nyx /app /home/nyx
USER nyx

# Health check (Railway sets PORT dynamically; default to 5000 locally)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c "python -c \"import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.getenv('PORT','5000')}/health')\""

# Expose port
EXPOSE 5000

# Render/Railway set PORT env var dynamically. Default to 5000 for local.
# Workers: 1 on free tier (memory), 2+ on paid tiers.
CMD ["sh", "-c", "python -m uvicorn backend.server_v2:app --host 0.0.0.0 --port ${PORT:-5000} --workers ${UVICORN_WORKERS:-1}"]
