# Migration Atlas

**An NLP-powered knowledge graph and ML toolkit for U.S. immigration analysis.**

[![CI](https://github.com/YOUR_USERNAME/migration-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/migration-atlas/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Reframing immigration as a graph: countries, visa pathways, landmark legislation, industries, and the economic threads that connect them — with four trained models on top.

---

## What this project is

Migration Atlas treats U.S. immigration as a **relational structure** rather than a collection of disconnected statistics. Origin countries are nodes. Laws that enabled or restricted them are edges. Visa pathways are typed connections. Industries of settlement are downstream nodes. On top of that graph sit four ML models that turn the data into something queryable, predictive, and analyzable.

This is a portfolio / academic case study built to demonstrate competence across the ML stack: data engineering, knowledge representation, classical NLP, transformer fine-tuning, retrieval-augmented generation, time-series forecasting, and graph machine learning.

## The four models

| # | Model | Purpose | Stack |
|---|-------|---------|-------|
| 1 | **Stance Classifier** | Score immigration legislation on four axes (restrictiveness, enforcement, legalization stance, humanitarian framing) | DistilBERT, fine-tuned on hand-labeled corpus |
| 2 | **Research Paper RAG** | Evidence-grounded answers from immigration economics literature (Borjas, Card, Peri, Cato, NAS, MPI, Pew) | sentence-transformers + ChromaDB + Claude API |
| 3 | **Flow Forecaster** | Predict country-of-origin migration flows for the next 1–5 years | Prophet + LSTM ensemble, with macro covariates |
| 4 | **Graph Embeddings** | Country/visa/law similarity and link prediction | Node2Vec on the knowledge graph |

All four feed a single React + D3 frontend with a natural-language query bar.

## Quick start

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/migration-atlas.git
cd migration-atlas
make setup              # creates venv, installs deps, downloads spaCy model

# Build the data + graph
make data               # downloads & processes Census ACS, USCIS, MPI data
make graph              # builds the knowledge graph from processed data

# Train the models (compute-aware — see Compute Plan below)
make train-stance       # ~30 min on Colab T4
make train-forecast     # ~5 min on CPU
make embeddings         # ~2 min on CPU
make rag-index          # ~10 min, ingests papers in data/corpus/

# Run the app
make app                # starts FastAPI backend + dev frontend
# → http://localhost:8000
```

## Compute plan (for the compute-constrained)

This project is designed to run end-to-end on **free Colab T4 + a laptop**. Where compute is needed, it's optional — you can use pre-trained checkpoints we publish via HuggingFace Hub.

| Task | Local CPU | Colab Free (T4) | Recommendation |
|------|-----------|-----------------|----------------|
| Stance classifier fine-tune | ❌ too slow | ✅ ~30 min | Train on Colab, push to Hub |
| RAG indexing | ✅ ~10 min | ✅ ~3 min | Local is fine |
| Forecaster (Prophet) | ✅ ~5 min | ✅ ~5 min | Local |
| Forecaster (LSTM ensemble) | ⚠️ ~1 hour | ✅ ~10 min | Colab if iterating |
| Graph embeddings | ✅ ~2 min | ✅ ~1 min | Local |
| Inference / app serving | ✅ | — | Local or HF Spaces |

For experiment tracking, we support two backends — pick whichever your free tier allows:
- **Weights & Biases** (default; `wandb.init()` only if `WANDB_API_KEY` is set)
- **MLflow** (local file backend, zero infra)
- **None** (just stdout logging — perfectly fine for a portfolio project)

## Repo structure

```
migration-atlas/
├── src/migration_atlas/        # main package (importable as migration_atlas)
│   ├── data/                   # ingestion + ETL for each source
│   ├── graph/                  # schema, build, traversal queries
│   ├── models/                 # the four models
│   │   ├── stance_classifier.py
│   │   ├── rag.py
│   │   ├── forecaster.py
│   │   └── graph_embeddings.py
│   ├── nlp/                    # query routing, entity extraction
│   ├── api/                    # FastAPI backend
│   └── utils/                  # config, logging
├── app/                        # React + D3 frontend (the interactive prototype)
├── notebooks/                  # exploratory + training walkthroughs
├── tests/                      # pytest suite (run with `make test`)
├── data/
│   ├── raw/                    # gitignored — populated by `make data`
│   ├── processed/              # parquet outputs
│   └── corpus/                 # research papers for RAG (PDF/MD)
├── configs/                    # YAML configs for each model
├── docs/                       # MkDocs site (run `make docs-serve`)
├── scripts/                    # one-off CLIs (download, eval, demo)
├── .github/workflows/          # CI: pytest, lint, type-check
├── Dockerfile                  # reproducible container
├── docker-compose.yml          # backend + Neo4j + frontend
├── Makefile                    # one-line entry points for everything
└── pyproject.toml              # project metadata
```

## Documentation

A full MkDocs site lives in `docs/`. Run locally:

```bash
make docs-serve
# → http://localhost:8001
```

Highlights:
- **Architecture** — four-layer system design, schema, edge types
- **Data sources** — what each source provides, update cadence, harmonization rules
- **Models** — training data, hyperparameters, evaluation metrics, known failure modes
- **API reference** — auto-generated from docstrings

## Demo deployment

The system is split for deployment:

- **Frontend** (`app/`) → **Vercel** (free, zero config). See [`docs/deploy/vercel.md`](docs/deploy/vercel.md).
- **Backend + RAG** → **HuggingFace Spaces** (free GPU tier). See [`docs/deploy/hf-spaces.md`](docs/deploy/hf-spaces.md).
- **Graph store** → **Neo4j Aura free tier** or in-process **NetworkX** (default). See [`docs/deploy/neo4j.md`](docs/deploy/neo4j.md).

A live demo URL will be added here once deployed: `https://migration-atlas.vercel.app` (placeholder).

## Data sources

| Source | What we use | Cadence |
|--------|-------------|---------|
| U.S. Census ACS | Foreign-born population by origin, year of entry, education, industry, geography | Annual |
| USCIS / OHSS Yearbook | Visa issuance, adjustments, naturalizations | Annual |
| Migration Policy Institute | Pre-aggregated tabulations, historical series | Continuous |
| Pew Research | Augmented unauthorized estimates, analytical deep-dives | Periodic |
| BLS | Labor force participation, industry / occupation | Monthly |
| OECD DIOC | Brain-drain measurement | ~5-year |
| Cato / NFAP / NAS | Fiscal contribution and entrepreneurship analyses | Periodic |
| Curated legal corpus | Federal + state immigration laws (full text) | Manual |

See [`data/README.md`](data/README.md) for the full data dictionary, harmonization decisions, and licensing notes for each source.

## Limitations & honest caveats

- **Definitional drift.** "Immigrant," "foreign-born," "unauthorized," and "refugee" are defined differently across sources. The pipeline harmonizes where possible and flags where it cannot.
- **Recent data lag.** Country-of-origin breakdowns lag the present by 12–18 months. Most figures use 2023 ACS.
- **Causal inference.** The graph captures association and known historical causation, not causal claims about wage / labor effects. Where economic claims are causal, they cite specific peer-reviewed studies.
- **Sentiment subjectivity.** The four-axis stance scoring is interpretive. We report inter-rater reliability against a 10% held-out sample.
- **Forecast horizons.** Beyond 5 years, predictions are unreliable. We report prediction intervals, not point estimates, and the app surfaces them.

## Citation

If this project is useful in your own work:

```bibtex
@software{migration_atlas_2026,
  author = {Your Name},
  title  = {Migration Atlas: An NLP-Powered Knowledge Graph of U.S. Immigration},
  year   = {2026},
  url    = {https://github.com/YOUR_USERNAME/migration-atlas}
}
```

## License

MIT. See [LICENSE](LICENSE).

---

*Built as an academic case study. Not affiliated with any government agency or research institution.*
