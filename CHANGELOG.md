# Changelog

## [Unreleased] — Phase B in progress

### Added — backend (Phase B)
- Graph schema: four new node kinds (`party-platform`, `legislator`, `news-org`, `discourse-event`) and four new edge kinds (`said-by`, `affiliated-with`, `targets`, `responds-to`).
- Pydantic property models for the new node kinds, including a four-axis sentiment score on `discourse-event`.
- `data/sources/voteview.py` — Voteview / DW-NOMINATE legislator ingest.
- `data/sources/manifesto.py` — Comparative Manifesto Project party-platform parser with per-platform immigration score.
- `data/sources/historical_press.py` — Chronicling America (Library of Congress) historical-newspaper search across seven default queries.
- `data/sources/hate_speech.py` — unified loader for HateXplain, Davidson 2017, and Founta 2018.
- `models/discourse/sentiment.py` — multi-axis discourse sentiment classifier (DistilBERT + four sigmoid heads).
- `POST /sentiment` endpoint with graceful degradation when the checkpoint is missing.
- Per-source tests for voteview, manifesto, and historical-press parsing.

### Added — frontend (Phase E foundation)
- `react-router-dom` integration. `App.jsx` is now a shell with a routed view outlet.
- Six named views (`Atlas`, `Forecast`, `Discourse`, `Simulate`, `Library`, `Timeline`).
- `Atlas` view ports the original graph experience.
- `Forecast` view: country selector, horizon slider, D3 prediction-interval chart, results table — wired to `/forecast/{country}`.
- `Discourse`, `Simulate`, `Library`, `Timeline` views shipped as static structural mockups; wire to live endpoints as Phase B/C/D models land.
- `api.sentiment(text)` client method.

### Added — docs
- Phase B section in `data/README.md` documenting Voteview, Manifesto, Chronicling America, hate-speech corpora.
- `POST /sentiment` documented in `docs/reference/api.md`.

## [0.2.0] — 2026-04-29 (Phase A.5: real data)
### Added
- Per-source ingest modules: Census ACS B05006, USCIS Yearbook Table 3, BLS labor force, Pew unauthorized estimates, MPI Data Hub.
- `data/country_codes.py` cross-source country registry.
- `data/process.py` harmonizer with USCIS-yearbook → ACS-delta flow priority.
- `Settings.census_api_key`, `Settings.bls_api_key`, configurable Census vintage.
- `openpyxl` dependency for XLSX ingest.

### Changed
- Architecture document rewritten for the five-layer (data / graph / models / simulation / app) platform vision.

## [0.1.0] — 2026-04-26 (Phase 1: foundation)
### Added
- 22-country, 9-visa, 8-law, 5-industry knowledge graph (44 nodes, 53 edges).
- Four base models: stance classifier, RAG, flow forecaster, graph embeddings.
- FastAPI backend with `/health`, `/graph`, `/query`, `/forecast`, `/similar` endpoints.
- React + D3 frontend with offline fallback bundle.
- MkDocs site, GitHub Actions CI (ruff, black, mypy, pytest matrix, docker, mkdocs --strict), Docker scaffolding.
