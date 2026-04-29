# Migration Atlas — multi-stage Dockerfile
# Builds a slim runtime image with the package and the FastAPI server.

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps for ML wheels (torch, prophet)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install into a venv we can copy across stages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel \
    && pip install -e . \
    && python -m spacy download en_core_web_sm

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Non-root user
RUN useradd --create-home --shell /bin/bash atlas

WORKDIR /home/atlas/app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/src /home/atlas/app/src
COPY configs/ /home/atlas/app/configs/

RUN chown -R atlas:atlas /home/atlas/app
USER atlas

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

CMD ["uvicorn", "migration_atlas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
