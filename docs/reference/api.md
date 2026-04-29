# API reference

The FastAPI backend exposes these endpoints. Auto-generated OpenAPI docs are available at `http://localhost:8000/docs` when the server is running.

## `GET /health`
Liveness check.
```json
{"status": "ok"}
```

## `GET /graph`
Return the full knowledge graph.
```json
{
  "nodes": [{"id": "mexico", "name": "Mexico", "kind": "country", ...}],
  "links": [{"source": "india", "target": "h-1b", "kind": "uses-visa", ...}]
}
```

## `POST /query`
Run a natural-language query.

Request:
```json
{"query": "How is India connected to the H-1B program?"}
```

Response:
```json
{
  "handler": "graph_lookup",
  "entities": ["india", "h-1b"],
  "answer": "Returning the sub-graph centered on india, h-1b: ...",
  "sub_graph": {"nodes": [...], "links": [...]}
}
```

The response shape varies by handler:
- `graph_lookup` → `sub_graph` is populated
- `forecast` → `forecast` is populated with the time series
- `similarity` → `similar` is populated with ranked nodes
- `rag` → `answer` contains the synthesized response

## `GET /forecast/{country}?horizon=5`
Get a precomputed forecast for one country.

## `GET /similar/{node_id}?top_k=10`
Get the top-k most similar nodes by graph embedding.

## `POST /sentiment` (Phase B)
Score a single piece of text on the four discourse axes.

Request:
```json
{"text": "Section 287(g) authorizes state and local enforcement..."}
```

Response:
```json
{
  "text": "Section 287(g) authorizes state and local enforcement...",
  "scores": {
    "hostile": 0.62,
    "welcoming": 0.08,
    "dehumanizing": 0.31,
    "assimilationist": 0.45
  },
  "model_loaded": true
}
```

When the discourse-sentiment checkpoint is missing (Phase B model not yet trained), the endpoint returns zero scores with `model_loaded: false` so the frontend can render an honest placeholder rather than receiving a 5xx.
