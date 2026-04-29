# Migration Atlas

**An NLP-powered knowledge graph and ML toolkit for U.S. immigration analysis.**

Migration Atlas treats U.S. immigration as a **relational structure** rather than a collection of disconnected statistics. Origin countries are nodes. Laws that enabled or restricted them are edges. Visa pathways are typed connections. Industries of settlement are downstream nodes. On top of that graph sit four ML models.

## The four models

| Model | Purpose |
|-------|---------|
| [Stance Classifier](models/stance.md) | Score immigration legislation on four axes |
| [Research Paper RAG](models/rag.md) | Evidence-grounded answers from the literature |
| [Flow Forecaster](models/forecaster.md) | Predict country-of-origin flows for the next 1–5 years |
| [Graph Embeddings](models/embeddings.md) | Country/visa/law similarity and link prediction |

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/migration-atlas.git
cd migration-atlas
make setup
make data graph
make train-all
make app
```

## Where to go next

- [Architecture overview](architecture.md) — the four layers and how they fit together
- [Data sources](data-sources.md) — what we ingest, how we harmonize
- [Deploy guides](deploy/vercel.md) — get a live demo URL
