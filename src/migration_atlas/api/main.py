"""FastAPI backend for Migration Atlas.

Serves three endpoints to the React frontend:

    GET  /health                     → liveness check
    GET  /graph                      → full knowledge graph as JSON
    POST /query                      → run a natural-language query
    GET  /forecast/{country}         → forecasted flows
    GET  /similar/{node_id}          → most similar nodes (graph embeddings)

The query endpoint is the unified entry point; it runs through `nlp.router.parse_query`
and dispatches to the right model.
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from migration_atlas.graph.build import build_default
from migration_atlas.nlp import parse_query
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)


# ============================================================
# App state (cached on startup)
# ============================================================
class AppState:
    graph_json: dict[str, Any] = {}
    forecasts: dict[str, list[dict]] = {}


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the graph and any precomputed forecasts on startup."""
    settings = get_settings()
    log.info("Loading graph...")
    backend = build_default()
    g = backend.graph
    state.graph_json = {
        "nodes": [{"id": nid, **dict(g.nodes[nid])} for nid in g.nodes],
        "links": [
            {"source": u, "target": v, "kind": k, **attrs}
            for u, v, k, attrs in g.edges(keys=True, data=True)
        ],
    }
    log.info("Graph loaded: %d nodes, %d links",
             len(state.graph_json["nodes"]), len(state.graph_json["links"]))

    # Optional: precomputed forecasts
    fc_path = settings.forecast_model_path / "forecasts.parquet"
    if fc_path.exists():
        try:
            import pandas as pd
            df = pd.read_parquet(fc_path)
            for country, sub in df.groupby("country"):
                state.forecasts[country] = sub.assign(
                    year=sub["year"].astype(str)
                ).to_dict(orient="records")
            log.info("Loaded forecasts for %d countries", len(state.forecasts))
        except Exception as e:
            log.warning("Could not load forecasts: %s", e)

    yield


app = FastAPI(
    title="Migration Atlas API",
    description="NLP-powered knowledge graph of U.S. immigration",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Schemas
# ============================================================
class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    handler: str
    entities: list[str]
    horizon: int | None = None
    answer: str | None = None
    sub_graph: dict[str, Any] | None = None
    forecast: list[dict] | None = None
    similar: list[dict] | None = None


class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    scores: dict[str, float]
    model_loaded: bool


# ============================================================
# Endpoints
# ============================================================
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/graph")
def get_graph() -> dict[str, Any]:
    if not state.graph_json:
        raise HTTPException(503, "Graph not yet loaded")
    return state.graph_json


@app.post("/query", response_model=QueryResponse)
def run_query(req: QueryRequest) -> QueryResponse:
    plan = parse_query(req.query)

    if plan.handler == "graph_lookup":
        sub = _extract_subgraph(plan.entities)
        return QueryResponse(
            handler=plan.handler,
            entities=plan.entities,
            sub_graph=sub,
            answer=_describe_subgraph(plan.entities, sub),
        )

    if plan.handler == "forecast":
        if not plan.entities:
            return QueryResponse(handler=plan.handler, entities=[],
                                 answer="Couldn't identify a country. Try 'forecast Mexico in 5 years'.")
        country = plan.entities[0]
        fc = state.forecasts.get(country, [])
        if not fc:
            return QueryResponse(handler=plan.handler, entities=plan.entities,
                                 answer=f"No forecast available for '{country}'. Run `make train-forecast`.")
        horizon = plan.horizon or 5
        return QueryResponse(
            handler=plan.handler,
            entities=plan.entities,
            horizon=horizon,
            forecast=fc[:horizon],
            answer=f"Forecast for {country} over the next {horizon} years.",
        )

    if plan.handler == "similarity":
        if not plan.entities:
            return QueryResponse(handler=plan.handler, entities=[],
                                 answer="Couldn't identify a node to compare against.")
        try:
            from migration_atlas.models.graph_embeddings import most_similar
            results = most_similar(plan.entities[0], top_k=plan.top_k)
            return QueryResponse(
                handler=plan.handler,
                entities=plan.entities,
                similar=[{"id": n, "score": s} for n, s in results],
                answer=f"Nodes most similar to '{plan.entities[0]}'.",
            )
        except (ImportError, KeyError, FileNotFoundError) as e:
            return QueryResponse(handler=plan.handler, entities=plan.entities,
                                 answer=f"Embeddings unavailable: {e}. Run `make embeddings`.")

    if plan.handler == "rag":
        try:
            from migration_atlas.models.rag import RagConfig, retrieve, synthesize
            cfg = RagConfig.from_yaml("configs/rag.yaml")
            hits = retrieve(req.query, cfg)
            answer = synthesize(req.query, hits, cfg)
            return QueryResponse(handler=plan.handler, entities=plan.entities, answer=answer)
        except Exception as e:
            return QueryResponse(handler=plan.handler, entities=plan.entities,
                                 answer=f"RAG unavailable: {e}. Run `make rag-index`.")

    return QueryResponse(handler=plan.handler, entities=plan.entities,
                         answer="Unknown handler.")


@app.get("/forecast/{country}")
def get_forecast(country: str, horizon: int = 5) -> dict[str, Any]:
    fc = state.forecasts.get(country)
    if not fc:
        raise HTTPException(404, f"No forecast for {country}")
    return {"country": country, "horizon": horizon, "forecast": fc[:horizon]}


@app.get("/similar/{node_id}")
def get_similar(node_id: str, top_k: int = 10) -> dict[str, Any]:
    from migration_atlas.models.graph_embeddings import most_similar
    try:
        results = most_similar(node_id, top_k)
    except (KeyError, FileNotFoundError) as e:
        raise HTTPException(404, str(e))
    return {"node": node_id, "similar": [{"id": n, "score": s} for n, s in results]}


# ============================================================
# Helpers
# ============================================================
def _extract_subgraph(entity_ids: list[str]) -> dict[str, Any]:
    """Return the sub-graph induced by the given nodes and their 1-hop neighbors."""
    if not entity_ids:
        return {"nodes": [], "links": []}
    nodes = state.graph_json["nodes"]
    links = state.graph_json["links"]
    keep = set(entity_ids)
    for link in links:
        if link["source"] in entity_ids:
            keep.add(link["target"])
        if link["target"] in entity_ids:
            keep.add(link["source"])
    sub_nodes = [n for n in nodes if n["id"] in keep]
    sub_links = [l for l in links if l["source"] in keep and l["target"] in keep]
    return {"nodes": sub_nodes, "links": sub_links}


def _describe_subgraph(entity_ids: list[str], sub: dict[str, Any]) -> str:
    if not entity_ids:
        return "No specific entities matched. Try a more specific query."
    primary = ", ".join(entity_ids)
    n_nodes = len(sub["nodes"])
    n_links = len(sub["links"])
    return (
        f"Returning the sub-graph centered on {primary}: "
        f"{n_nodes} nodes and {n_links} relationships."
    )
