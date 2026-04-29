# Hugging Face Spaces Dockerfile for Migration Atlas backend.
#
# Differences from the root Dockerfile:
#   - HF Spaces requires the app to listen on $PORT (default 7860).
#   - The runtime user is 'user' with HOME=/home/user (HF convention).
#   - Models / cached datasets land under /home/user/.cache.
#
# Push the contents of this directory to your Space repo:
#   huggingface-cli login
#   git clone https://huggingface.co/spaces/<your-handle>/migration-atlas hf-space
#   cp -r deploy/hf-spaces/* hf-space/
#   cp -r src configs hf-space/
#   cd hf-space && git add . && git commit -m "deploy" && git push

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces convention: non-root user 'user'
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" \
    HOME=/home/user

WORKDIR /home/user/app

COPY --chown=user pyproject.toml README.md ./
COPY --chown=user src/ ./src/
COPY --chown=user configs/ ./configs/

RUN pip install --user --upgrade pip setuptools wheel \
    && pip install --user -e . \
    && python -m spacy download en_core_web_sm

EXPOSE 7860

CMD ["uvicorn", "migration_atlas.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
