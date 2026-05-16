# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./

# Media directory — will be overridden by volume mount in production
# but created here so the image starts cleanly if no volume is attached
RUN mkdir -p /media/sections /media/uploads /media/tmp \
    && chown -R appuser:appuser /media

USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--loop", "uvloop", "--http", "httptools"]