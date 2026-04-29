---
title: Migration Atlas
emoji: 🌐
colorFrom: orange
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Migration Atlas — backend on Hugging Face Spaces

The FastAPI backend for [Migration Atlas](https://github.com/ujjawal40/migration-atlas), packaged as a Docker Space.

## What this Space serves

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check |
| `GET /graph` | Full knowledge graph as JSON |
| `POST /query` | Natural-language router (graph / forecast / similarity / RAG) |
| `GET /forecast/{country}` | Pre-computed flow forecasts |
| `GET /similar/{node_id}` | Graph-embedding similarity |
| `POST /sentiment` | Discourse sentiment scoring (Phase B) |

The frontend is hosted separately on Vercel and reaches this Space via `VITE_API_URL`.

## Configuration

Add these as Space secrets if you want full functionality:

| Secret | Effect |
|---|---|
| `ANTHROPIC_API_KEY` | Enables RAG synthesis (otherwise returns ranked passages) |
| `CENSUS_API_KEY` | Required only if you want the Space to refresh data on boot |

Without secrets the API still serves the seed graph and any models that have checkpoints baked into the image.
