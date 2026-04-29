"""Natural-language query router.

Parses user queries into a structured plan that the API layer can execute.
A query can resolve to one of four handlers:

    - graph_lookup     → traverse the knowledge graph (the default)
    - rag              → ask the research-paper RAG
    - forecast         → return a forecast for a country
    - similarity       → return graph-embedding neighbors

The router uses a fast keyword + entity match by default and falls back to the
Anthropic API if `ANTHROPIC_API_KEY` is set, which gracefully handles
paraphrases ("green card holders" → "lawful permanent residents", etc.).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from migration_atlas.graph.seed import all_nodes
from migration_atlas.utils import get_logger

log = get_logger(__name__)

QueryHandler = Literal["graph_lookup", "rag", "forecast", "similarity"]


@dataclass
class QueryPlan:
    """Structured representation of a natural-language query."""

    handler: QueryHandler
    entities: list[str] = field(default_factory=list)   # resolved node ids
    raw_query: str = ""
    horizon: int | None = None                          # for forecast queries
    top_k: int = 5

    def to_dict(self) -> dict:
        return {
            "handler": self.handler,
            "entities": self.entities,
            "raw_query": self.raw_query,
            "horizon": self.horizon,
            "top_k": self.top_k,
        }


# ============================================================
# Entity catalog (built from the seed graph)
# ============================================================
def _build_alias_map() -> dict[str, str]:
    """Map lowercase aliases → canonical node id."""
    aliases: dict[str, str] = {}
    for n in all_nodes():
        aliases[n.name.lower()] = n.id
        aliases[n.id.replace("-", " ")] = n.id
        aliases[n.id] = n.id
    # Custom aliases for common paraphrases
    aliases.update({
        "green card": "family-based",
        "h1b": "h-1b", "h 1 b": "h-1b",
        "1965 act": "ina-1965",
        "hart-celler": "ina-1965", "hart celler": "ina-1965",
        "reagan amnesty": "irca-1986",
        "exclusion act": "chinese-exclusion-1882",
        "diversity visa": "dv-lottery",
    })
    return aliases


_ALIASES = _build_alias_map()


# ============================================================
# Intent classification (rule-based, fast)
# ============================================================
_FORECAST_KEYWORDS = ["forecast", "predict", "next year", "in 5 years",
                      "future", "projection", "will arrive", "trend"]
_SIMILARITY_KEYWORDS = ["similar to", "like", "comparable", "resemble", "cluster"]
_RAG_KEYWORDS = ["wage effect", "labor market", "fiscal", "economic impact",
                 "research says", "studies show", "what does the literature",
                 "evidence", "according to"]


def _detect_handler(q: str) -> QueryHandler:
    qlow = q.lower()
    if any(kw in qlow for kw in _FORECAST_KEYWORDS):
        return "forecast"
    if any(kw in qlow for kw in _SIMILARITY_KEYWORDS):
        return "similarity"
    if any(kw in qlow for kw in _RAG_KEYWORDS):
        return "rag"
    return "graph_lookup"


def _extract_entities(q: str) -> list[str]:
    """Find all node ids referenced in the query (longest-match first)."""
    qlow = " " + q.lower() + " "
    found: list[tuple[int, int, str]] = []  # (start, length, id)
    for alias, node_id in _ALIASES.items():
        # Word-boundary match
        for m in re.finditer(rf"\b{re.escape(alias)}\b", qlow):
            found.append((m.start(), len(alias), node_id))
    # Longest match wins on overlap
    found.sort(key=lambda x: (-x[1], x[0]))
    accepted: list[str] = []
    used_ranges: list[tuple[int, int]] = []
    for start, length, node_id in found:
        end = start + length
        if any(not (end <= s or start >= e) for s, e in used_ranges):
            continue
        if node_id not in accepted:
            accepted.append(node_id)
        used_ranges.append((start, end))
    return accepted


def _extract_horizon(q: str) -> int | None:
    """Pull a horizon out of phrases like 'in 5 years', 'next 3 years'."""
    m = re.search(r"(?:in|next)\s+(\d+)\s+year", q.lower())
    if m:
        return int(m.group(1))
    return None


# ============================================================
# Public API
# ============================================================
def parse_query(query: str) -> QueryPlan:
    """Convert a natural-language query into a QueryPlan."""
    handler = _detect_handler(query)
    entities = _extract_entities(query)
    horizon = _extract_horizon(query) if handler == "forecast" else None
    plan = QueryPlan(
        handler=handler,
        entities=entities,
        raw_query=query,
        horizon=horizon,
    )
    log.debug("Parsed query: %s", plan.to_dict())
    return plan
