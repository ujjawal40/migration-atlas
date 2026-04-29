# Migration Atlas — LLM Context File

> **For the model reading this:** this is a complete project briefing. After reading it, you should be able to answer architectural questions, generate new code that fits the existing conventions, modify any layer without breaking the others, and pick up a half-finished task. Read it once carefully — it replaces a long conversation history.

---

## 1. Project at a glance

**Name:** Migration Atlas
**Type:** Academic case study + portfolio piece
**Domain:** U.S. immigration (knowledge graph, NLP, ML)
**Stack:** Python 3.10+, FastAPI, React 18, D3.js, Neo4j (optional)
**Repo layout:** Monorepo (`src/` Python package + `app/` React frontend)
**License:** MIT
**Status:** Phase 1 complete (scaffold + working prototype). Phases 2 and 3 pending.

**One-line elevator pitch:** Treat U.S. immigration as a relational graph (countries × visas × laws × industries) with four ML models layered on top — a stance classifier on legislation, RAG over research papers, a flow forecaster, and graph embeddings.

**The three reasons this project exists, in priority order:**

1. Demonstrate ML-stack range across a realistic domain (data eng, NLP, fine-tuning, RAG, time-series, graph ML).
2. Produce a polished portfolio artifact — repo + live demo + writeup — for academic and industry audiences.
3. Actually answer interesting questions about U.S. immigration using a graph+ML approach that no single dataset supports.

---

## 2. The four-layer architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: APP                                                │
│   FastAPI backend (src/migration_atlas/api/main.py)         │
│   React + D3 frontend (app/src/)                            │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│ Layer 3: MODELS (the four ML models)                        │
│   • Stance classifier   — DistilBERT + 4 regression heads   │
│   • Research RAG        — sentence-transformers + ChromaDB  │
│   • Flow forecaster     — Prophet + LSTM ensemble           │
│   • Graph embeddings    — Node2Vec                          │
│   NLP router (src/migration_atlas/nlp/router.py)            │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│ Layer 2: GRAPH                                              │
│   NetworkX backend (default, in-memory)                     │
│   Neo4j backend (production, persistent)                    │
│   Schema in src/migration_atlas/graph/schema.py             │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│ Layer 1: DATA                                               │
│   Census ACS, USCIS, MPI, BLS, OECD, Pew, legal corpus      │
│   Outputs as Parquet in data/processed/                     │
└─────────────────────────────────────────────────────────────┘
```

**Layer contracts (these are firm):**

- Data layer never imports from models or app.
- Model layer never assumes a specific graph backend (it goes through `migration_atlas.graph`).
- App layer never reaches into model internals — only through `/query` and the typed API endpoints.
- Each model is independently runnable via its own Typer CLI.

---

## 3. Data stores

| Store                  | What                     | Why this choice                                 | Where                                                      |
| ---------------------- | ------------------------ | ----------------------------------------------- | ---------------------------------------------------------- |
| **NetworkX** (default) | Knowledge graph          | In-memory, zero infra, ~50 nodes fits trivially | `migration_atlas.graph.NetworkXBackend`                    |
| **Neo4j** (optional)   | Knowledge graph at scale | Cypher, GDS plugin, persistence                 | `migration_atlas.graph.Neo4jBackend`, `docker-compose.yml` |
| **Parquet**            | Tabular ETL outputs      | Columnar, read-heavy, engine-agnostic           | `data/processed/*.parquet`                                 |
| **ChromaDB**           | RAG vector index         | Lightweight, local persist, swappable           | `chroma_db/`                                               |
| **Files + HF Hub**     | Model checkpoints        | Standard ML artifact pattern                    | `checkpoints/` (gitignored)                                |

**No PostgreSQL, no MongoDB, no Redis, no Elasticsearch.** Each was deliberately rejected — see `docs/architecture.md` for reasoning if asked.

---

## 4. Knowledge graph schema (memorize this)

### Node kinds (5)

| Kind       | Examples                                    | Key properties                                               |
| ---------- | ------------------------------------------- | ------------------------------------------------------------ |
| `country`  | mexico, india, china, vietnam               | foreign_born_us, immigrant_share, top_destination_state, era |
| `visa`     | h-1b, f-1, eb-5, family-based, tps          | annual_cap, year_established, top_country                    |
| `law`      | ina-1965, irca-1986, immigration-act-1990   | year*enacted, year_repealed, stance*\* (4 axes)              |
| `industry` | tech, healthcare, construction, agriculture | immigrant_share, unauthorized_share                          |
| `region`   | (state-level — not yet populated)           | foreign_born_share                                           |

### Edge kinds (8, directed)

| Edge         | From → To          | Semantic                                  |
| ------------ | ------------------ | ----------------------------------------- |
| `uses-visa`  | country → visa     | Country's nationals heavily use this visa |
| `enables`    | law → country/visa | Law made this corridor or visa possible   |
| `restricts`  | law → country      | Law limited migration from this origin    |
| `creates`    | law → visa         | Law established this visa category        |
| `legalized`  | law → country      | Law granted retroactive legal status      |
| `works-in`   | country → industry | Concentration ratio                       |
| `settles-in` | country → region   | Settlement share                          |
| `amends`     | law → law          | Later law modified earlier one            |

### Stable IDs

All node IDs are **lowercase, hyphenated, no spaces**. Validated by Pydantic in `schema.py`. Examples: `el-salvador`, `ina-1965`, `chinese-exclusion-1882`, `dv-lottery`. Aliases (e.g., "Hart-Celler" → `ina-1965`) live in `nlp/router.py::_build_alias_map()`.

### Seed counts

44 nodes (22 countries + 9 visas + 8 laws + 5 industries) and 53 edges. Seed data lives in `src/migration_atlas/graph/seed.py` and is the single source of truth until ETL replaces it.

---

## 5. The four models — what each does, where to find it

### Model 1: Stance Classifier

**File:** `src/migration_atlas/models/stance_classifier.py`
**Config:** `configs/stance.yaml`
**Purpose:** Score immigration legislation on four orthogonal axes — restrictiveness, enforcement, legalization, humanitarian — each in [0, 1].
**Architecture:** Shared DistilBERT encoder → 4 sigmoid regression heads.
**Training:** ~30 min on Colab T4. Synthetic seed data in `notebooks/02_stance_training.ipynb`; replace with ~500 hand-labeled section-level chunks for production.
**Inference:** `python -m migration_atlas.models.stance_classifier predict --text "..."`

### Model 2: Research Paper RAG

**File:** `src/migration_atlas/models/rag.py`
**Config:** `configs/rag.yaml`
**Purpose:** Evidence-grounded answers from immigration economics literature.
**Stack:** sentence-transformers (`all-MiniLM-L6-v2`) + ChromaDB. Synthesis via Anthropic Claude API if `ANTHROPIC_API_KEY` is set; falls back to ranked passages otherwise.
**Workflow:** Drop PDFs/MD/TXT into `data/corpus/` → `make rag-index` → query.

### Model 3: Flow Forecaster (the headline model)

**File:** `src/migration_atlas/models/forecaster.py`
**Config:** `configs/forecast.yaml`
**Purpose:** Predict country-of-origin migration flows for the next 1–5 years.
**Approach:** Prophet + lightweight LSTM ensemble, weighted by inverse held-out MAE. Synthetic flows generator (`_write_synthetic_flows`) keeps the pipeline runnable without real data.
**Output:** Parquet with columns `[year, country, yhat, yhat_lower, yhat_upper, model]`.

### Model 4: Graph Embeddings

**File:** `src/migration_atlas/models/graph_embeddings.py`
**Config:** `configs/embeddings.yaml`
**Purpose:** Country/visa/law similarity + link prediction.
**Stack:** Node2Vec on the undirected projection of the knowledge graph. 64-dim embeddings persisted as gensim `KeyedVectors`.
**Note:** GNNs (GraphSAGE/GAT) deliberately rejected — graph is too small (~50 nodes), they overfit immediately.

---

## 6. NLP query router

**File:** `src/migration_atlas/nlp/router.py`
**Function:** `parse_query(text: str) -> QueryPlan`

Routes a natural-language query to one of four handlers:

| Handler        | Triggered by keywords                                                | Dispatches to      |
| -------------- | -------------------------------------------------------------------- | ------------------ |
| `forecast`     | "forecast", "predict", "next year", "in 5 years"                     | Forecaster outputs |
| `similarity`   | "similar to", "like", "comparable", "resemble", "cluster"            | Graph embeddings   |
| `rag`          | "wage effect", "labor market", "fiscal", "research says", "evidence" | RAG model          |
| `graph_lookup` | (default)                                                            | Graph traversal    |

Entity extraction uses longest-match against the alias map (~50 entries: canonical names + IDs + custom aliases). Phase 3 will swap this for Claude API NER for paraphrase robustness.

---

## 7. The 42 economic metrics (catalog)

The case study tracks **42 metrics across 7 dimensions**. Full catalog with sources lives in the architecture doc (Section 4 of `Migration_Atlas_Architecture.docx`). Summary:

1. **Fiscal contribution** (7) — federal income tax, FICA, state/local tax, lifetime fiscal balance, public benefits utilization, public-good free-rider effect, cumulative fiscal surplus
2. **Labor market** (8) — labor force share, LFPR, industry concentration, complementarity, low-skill wage effect, high-skill wage effect, migration-driven wage dampening, vacancy fill rate
3. **Entrepreneurship & innovation** (6) — Fortune 500 founders, unicorn founders, patents per inventor, self-employment rate, STEM PhD share, Nobel share
4. **Macroeconomic aggregates** (6) — GDP contribution, counterfactual GDP, inflation effect, debt-to-GDP counterfactual, productivity growth, consumer spending
5. **Demographic & human capital** (6) — educational attainment, English proficiency, skill premium by origin, brain-drain intensity, second-generation outcomes, naturalization rate
6. **Industry & sectoral** (5) — construction unauthorized share, agricultural immigrant share, healthcare immigrant share, tech immigrant share, hospitality immigrant share
7. **Geographic concentration** (4) — state foreign-born share, metropolitan concentration, origin concentration ratio, settlement diversity index

---

## 8. Repo file map

```
migration-atlas/
├── README.md                           # Public-facing project overview
├── LICENSE                             # MIT
├── CONTRIBUTING.md                     # Dev workflow
├── pyproject.toml                      # Python package metadata, deps, tool configs
├── Makefile                            # Single-command interface (make setup, make train-all, etc.)
├── Dockerfile                          # Multi-stage build: builder → slim runtime
├── docker-compose.yml                  # Stack: api + neo4j + frontend
├── mkdocs.yml                          # Docs site config
├── .env.example                        # Env var template
├── .gitignore                          # Python + Node + ML artifacts + data
│
├── .github/workflows/
│   └── ci.yml                          # Lint + test (3.10, 3.11) + docs + docker build
│
├── src/migration_atlas/                # Main Python package
│   ├── __init__.py                     # Re-exports Settings, get_settings, __version__
│   ├── cli.py                          # Top-level Typer CLI: `migration-atlas <cmd>`
│   ├── utils/
│   │   ├── config.py                   # Pydantic-settings: paths, API keys, backends
│   │   └── logging.py                  # Rich-formatted logger
│   ├── data/
│   │   ├── download.py                 # Source registry; stub for Phase 3 ETL
│   │   ├── process.py                  # ETL stub
│   │   └── ingest_corpus.py            # PDF/MD/TXT → chunked Parquet
│   ├── graph/
│   │   ├── schema.py                   # Pydantic Node/Edge/GraphSpec + enums
│   │   ├── seed.py                     # 44-node, 53-edge seed graph
│   │   └── build.py                    # NetworkXBackend + Neo4jBackend + JSON export
│   ├── models/
│   │   ├── stance_classifier.py        # DistilBERT + 4 heads, full training loop
│   │   ├── rag.py                      # ChromaDB indexer + Claude synthesis
│   │   ├── forecaster.py               # Prophet + LSTM + ensemble
│   │   └── graph_embeddings.py         # Node2Vec wrapper
│   ├── nlp/
│   │   └── router.py                   # parse_query, alias map, intent rules
│   └── api/
│       └── main.py                     # FastAPI: /health, /graph, /query, /forecast/{c}, /similar/{n}
│
├── app/                                # React + Vite + D3 frontend
│   ├── package.json
│   ├── vite.config.js                  # Dev proxy: /api/* → localhost:8000
│   ├── index.html
│   ├── public/favicon.svg
│   └── src/
│       ├── main.jsx                    # React entry
│       ├── App.jsx                     # Top-level layout, state, query handling
│       ├── api.js                      # Fetch wrapper
│       ├── constants.js                # Colors, labels, presets, nodeRadius()
│       ├── fallbackData.js             # Bundled graph for offline/no-backend mode
│       ├── styles.css                  # Editorial / archival aesthetic
│       └── components/
│           ├── Graph.jsx               # D3 force-directed visualization
│           ├── QueryBar.jsx            # NL input + chips
│           ├── FilterPanel.jsx         # Left rail (kinds/edges/eras)
│           └── DetailPanel.jsx         # Right rail (selected node + query response)
│
├── configs/                            # YAML configs for each model
│   ├── stance.yaml
│   ├── rag.yaml
│   ├── forecast.yaml
│   └── embeddings.yaml
│
├── notebooks/                          # Runnable walkthroughs
│   ├── 01_eda.ipynb                    # Graph EDA, distributions, sanity checks
│   ├── 02_stance_training.ipynb        # Colab-ready training walkthrough
│   ├── 03_forecasting.ipynb            # Prophet + LSTM end-to-end
│   └── 04_graph_embeddings.ipynb       # Node2Vec + similarity + 2D PCA
│
├── tests/                              # pytest suite (run with `make test`)
│   ├── conftest.py
│   ├── test_schema.py                  # Pydantic validation
│   ├── test_build.py                   # Graph integrity
│   ├── test_nlp_router.py              # Parametrized: handlers, entities, horizons
│   └── test_api.py                     # FastAPI smoke tests via TestClient
│
├── data/
│   ├── README.md
│   ├── raw/                            # gitignored — populated by `make data`
│   ├── processed/                      # parquet outputs
│   └── corpus/                         # research papers for RAG
│
├── docs/                               # MkDocs Material site
│   ├── index.md
│   ├── architecture.md                 # System diagram + layer responsibilities
│   ├── data-sources.md                 # Per-source license + harmonization notes
│   ├── models/                         # One file per model
│   ├── deploy/                         # Vercel / HF Spaces / Neo4j
│   └── reference/api.md                # Endpoint docs
│
└── checkpoints/                        # gitignored — model weights
```

---

## 9. Conventions to preserve

When generating new code, match these:

**Python**

- Black, line length 100. Ruff for linting (`E`, `F`, `W`, `I`, `N`, `B`, `UP`, `SIM`).
- Mypy in warn-mode for now (`continue-on-error: true` in CI).
- `from __future__ import annotations` at the top of every file.
- Pydantic v2 (`model_config = SettingsConfigDict(...)`, not v1's `class Config`).
- Type hints on public functions; Google-style docstrings.
- Typer for CLIs, never argparse.
- Logging via `migration_atlas.utils.get_logger(__name__)`, never `print()` in library code.
- Settings via `get_settings()` (cached), never `os.environ` directly.
- Path objects, not strings.
- Dataclasses for configs (`@dataclass`), Pydantic for validated I/O.

**JavaScript/React**

- React 18 functional components with hooks. No class components.
- ESM modules; `.jsx` extension for components.
- D3 v7 (`import * as d3 from "d3"`).
- CSS custom properties for theming (the `--ink`, `--paper`, `--accent` system in `styles.css`).
- No CSS-in-JS, no Tailwind — handwritten CSS in `styles.css`.
- Prefer `useMemo`/`useEffect` cleanly separated; D3 mutations inside `useEffect` with proper cleanup.

**Aesthetic**

- Editorial / archival, not dashboard-y. Warm paper backgrounds (`#f5f1ea`), Fraunces serif for display, JetBrains Mono for metadata, deep orange (`#c2410c`) as the single accent. Sharp 1.5px ruled borders, no rounded corners except where unavoidable.
- Don't drift toward purple gradients, neon, or generic SaaS look.

**Comments**

- Module docstrings explain purpose + CLI invocation.
- Inline comments explain _why_, not _what_.
- Section banners (`# ============`) separate logical blocks in long files.

---

## 10. Phasing — where we are

| Phase                                   | Status      | Deliverables                                                                                                                                                 |
| --------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Phase 1: Foundation**                 | ✅ Complete | Architecture doc, schema, 42-metric catalog, working interactive prototype, full repo scaffold                                                               |
| **Phase 2: Case study writeup**         | ⏳ Pending  | Full academic-style writeup: lit review, methodology, country deep-dives, worked example queries, references                                                 |
| **Phase 3: Production NLP & sentiment** | ⏳ Pending  | Anthropic API integrated for real NL parsing; sentiment pipeline run on real legal corpus; Sankey + choropleth + legislative timeline views; Neo4j migration |

**Known gaps in current state:**

- Synthetic flows in forecaster (real USCIS/Census data pending)
- Synthetic stance training labels (real ~500-chunk corpus pending)
- Empty `data/corpus/` (research papers pending)
- ETL stubs in `data/download.py` and `data/process.py` (real fetchers pending)
- `YOUR_USERNAME` placeholder in README, mkdocs.yml, deploy guides
- Author/email placeholders in `pyproject.toml` and `LICENSE`

---

## 11. Common tasks — how to do them

**"Add a new country to the graph"**
→ Add a `Node` to `COUNTRIES` in `src/migration_atlas/graph/seed.py`. Add edges to relevant visas/laws/industries in `EDGES`. The graph rebuilds on next `make graph`.

**"Add a new visa type"**
→ Same pattern in `seed.py::VISAS`. If a law created it, add a `creates` edge.

**"Add a new ML model"**
→ Create `src/migration_atlas/models/<name>.py` matching the pattern of the existing four (config dataclass + train function + predict function + Typer CLI). Add config YAML in `configs/`. Wire to `/query` in `api/main.py`. Add docs page in `docs/models/`. Add tests.

**"Add a new data source"**
→ Per-source ingester in `src/migration_atlas/data/`. Document in `docs/data-sources.md` and `data/README.md`. Update graph builder if it contributes nodes/edges. Add smoke test.

**"Change the four stance axes"**
→ Edit `AXES` constant in `stance_classifier.py`. Update labels in `LawProperties` in `graph/schema.py`. Re-train with new labels. Update docs in `docs/models/stance.md`.

**"Switch to Neo4j"**
→ Set `GRAPH_BACKEND=neo4j` in `.env`. Bring up Neo4j with `docker-compose up neo4j`. Run `make graph` — the build script writes to Neo4j via `Neo4jBackend`.

**"Deploy the demo"**
→ Frontend to Vercel (root `app/`). Backend to HuggingFace Spaces with Docker SDK. See `docs/deploy/`.

---

## 12. Decisions you should not silently revert

These were chosen deliberately. Don't change them without explicit instruction:

- **Graph store: NetworkX as default**, Neo4j as opt-in. Don't make Neo4j required.
- **No relational DB.** The data is read-heavy and graph-shaped.
- **Node2Vec, not GNN.** The graph is too small (~50 nodes) for GNNs to add value over shallow embeddings.
- **Prophet + LSTM ensemble**, not just one. Each fails on different countries; ensemble robust to that.
- **DistilBERT for stance classifier**, not RoBERTa-large or GPT-style. Compute-constrained, Colab-T4 sized.
- **ChromaDB for vector store**, not Pinecone or Weaviate. Local-first, no infra.
- **Editorial aesthetic** in the frontend, not standard dashboard look. Differentiates from typical "data tool" portfolios.
- **Four stance axes** (restrictiveness, enforcement, legalization, humanitarian), not generic sentiment. Generic positive/negative is wrong for legal text.
- **MIT license**, not Apache 2.0 or GPL.
- **No proactive Anthropic API key requirement.** The system degrades gracefully without it (RAG returns ranked passages instead of synthesized answers).

---

## 13. Frequently-needed snippets

**Build the graph in code:**

```python
from migration_atlas.graph.build import build_default
backend = build_default()         # NetworkXBackend
g = backend.graph                  # nx.MultiDiGraph
```

**Parse a natural-language query:**

```python
from migration_atlas.nlp import parse_query
plan = parse_query("How is India connected to H-1B?")
# QueryPlan(handler='graph_lookup', entities=['india', 'h-1b'], ...)
```

**Run any model's CLI:**

```bash
python -m migration_atlas.models.stance_classifier train --config configs/stance.yaml
python -m migration_atlas.models.forecaster predict --country mexico --horizon 5
python -m migration_atlas.models.graph_embeddings similar --node india --top-k 10
python -m migration_atlas.models.rag query --q "wage effect of low-skill immigration"
```

**Import settings:**

```python
from migration_atlas.utils import get_settings, get_logger
settings = get_settings()
log = get_logger(__name__)
```

---

## 14. What to optimize for in suggestions

If asked to extend the project:

1. **Match existing conventions** (Section 9) before introducing anything new.
2. **Preserve layer boundaries** (Section 2). Don't have models import from API or vice versa.
3. **Add tests** for any new functionality. The existing pattern is in `tests/`.
4. **Update docs** in `docs/` and the relevant docstrings.
5. **Keep it Colab-runnable.** Compute is a real constraint here; don't suggest 7B-parameter fine-tunes.
6. **Honest caveats.** This is an academic project; be explicit about limitations of synthetic data, definitional drift, and 5-year forecast horizons.

---

## 15. Companion artifacts

- `Migration_Atlas_Architecture.docx` — full architecture & design document (Phase 1 deliverable)
- `migration_atlas_prototype.html` — standalone HTML version of the interactive graph (no build step)
- `migration-atlas.zip` — the full repo as a downloadable archive

---

_End of context file. Version: April 2026. Source of truth: this file, plus the repo it describes._
