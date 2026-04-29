# Migration Atlas — Makefile
# Single-command interface to the project. Run `make help` for the menu.

.PHONY: help setup install install-dev clean
.PHONY: data graph corpus
.PHONY: train-stance train-forecast embeddings rag-index train-all
.PHONY: app api frontend
.PHONY: test test-fast lint format type-check check
.PHONY: docs-serve docs-build
.PHONY: docker-build docker-up docker-down
.PHONY: deploy-frontend deploy-backend

# ----- Configuration -----
PYTHON       ?= python3
VENV         ?= .venv
PIP          := $(VENV)/bin/pip
PY           := $(VENV)/bin/python
PYTEST       := $(VENV)/bin/pytest
SHELL        := /bin/bash

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help menu
	@echo "Migration Atlas — Make targets"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ============================================================
# Setup
# ============================================================
setup: $(VENV)/bin/activate install-dev download-spacy  ## Full first-time setup
	@echo "✅ Setup complete. Activate with: source $(VENV)/bin/activate"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install:  ## Install runtime dependencies
	$(PIP) install -e .

install-dev:  ## Install development dependencies
	$(PIP) install -e ".[dev,docs,tracking]"

download-spacy:  ## Download spaCy English model
	$(PY) -m spacy download en_core_web_sm

clean:  ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ============================================================
# Data pipeline
# ============================================================
data:  ## Download + process all data sources
	$(PY) -m migration_atlas.data.download
	$(PY) -m migration_atlas.data.process

graph:  ## Build knowledge graph from processed data
	$(PY) -m migration_atlas.graph.build

corpus:  ## Ingest research papers from data/corpus/ into chunks
	$(PY) -m migration_atlas.data.ingest_corpus --src data/corpus --out data/processed/chunks.parquet

# ============================================================
# Model training
# ============================================================
train-all: train-stance train-forecast embeddings rag-index  ## Train all four models

train-stance:  ## Fine-tune the stance classifier (Colab T4 recommended)
	$(PY) -m migration_atlas.models.stance_classifier train --config configs/stance.yaml

train-sentiment:  ## Fine-tune the discourse sentiment classifier (Phase B)
	$(PY) -m migration_atlas.models.discourse.sentiment train --config configs/sentiment.yaml

train-forecast:  ## Train migration flow forecasters
	$(PY) -m migration_atlas.models.forecaster train --config configs/forecast.yaml

embeddings:  ## Compute Node2Vec embeddings on the knowledge graph
	$(PY) -m migration_atlas.models.graph_embeddings train --config configs/embeddings.yaml

rag-index:  ## Build the RAG vector index from data/corpus/
	$(PY) -m migration_atlas.models.rag index --config configs/rag.yaml

# ============================================================
# Run / serve
# ============================================================
app: api  ## Run the full app (API + frontend dev server)
	@echo "Frontend: cd app && npm run dev"

api:  ## Start the FastAPI backend
	$(PY) -m uvicorn migration_atlas.api.main:app --reload --port 8000

frontend:  ## Run frontend dev server (requires npm install in app/)
	cd app && npm run dev

# ============================================================
# Quality
# ============================================================
test:  ## Run full test suite with coverage
	$(PYTEST)

test-fast:  ## Run tests, excluding slow + integration
	$(PYTEST) -m "not slow and not integration"

lint:  ## Run ruff linter
	$(VENV)/bin/ruff check src tests

format:  ## Auto-format code with black + ruff
	$(VENV)/bin/black src tests
	$(VENV)/bin/ruff check --fix src tests

type-check:  ## Run mypy
	$(VENV)/bin/mypy src

check: lint type-check test  ## Run all quality checks

# ============================================================
# Docs
# ============================================================
docs-serve:  ## Serve the docs site locally
	$(VENV)/bin/mkdocs serve -a localhost:8001

docs-build:  ## Build the static docs site
	$(VENV)/bin/mkdocs build

# ============================================================
# Docker
# ============================================================
docker-build:  ## Build the Docker image
	docker build -t migration-atlas:latest .

docker-up:  ## Start full stack via docker-compose
	docker-compose up --build

docker-down:  ## Tear down docker-compose stack
	docker-compose down

# ============================================================
# Deploy
# ============================================================
deploy-frontend:  ## Deploy frontend to Vercel
	cd app && vercel --prod

deploy-backend:  ## Deploy backend to HuggingFace Spaces
	@echo "Push the contents of /deploy/hf-spaces/ to your Space repo. See docs/deploy/hf-spaces.md."
