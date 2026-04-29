"""Knowledge graph schema: node and edge type definitions.

The schema is the single source of truth for what the graph contains. Both the
NetworkX and Neo4j backends serialize against these types.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class NodeKind(str, Enum):
    COUNTRY = "country"
    VISA = "visa"
    LAW = "law"
    INDUSTRY = "industry"
    REGION = "region"
    # Phase B: discourse and political affiliation
    PARTY_PLATFORM = "party-platform"
    LEGISLATOR = "legislator"
    NEWS_ORG = "news-org"
    DISCOURSE_EVENT = "discourse-event"


class EdgeKind(str, Enum):
    USES_VISA = "uses-visa"
    ENABLES = "enables"
    RESTRICTS = "restricts"
    CREATES = "creates"
    LEGALIZED = "legalized"
    WORKS_IN = "works-in"
    SETTLES_IN = "settles-in"
    AMENDS = "amends"
    # Phase B: discourse and affiliation
    SAID_BY = "said-by"             # discourse-event → legislator / news-org / author
    AFFILIATED_WITH = "affiliated-with"  # legislator → party-platform
    TARGETS = "targets"             # discourse-event → country / visa / law
    RESPONDS_TO = "responds-to"     # discourse-event → law / discourse-event


class Node(BaseModel):
    """A graph node. The `id` is stable across runs and used as the primary key."""

    id: str = Field(..., min_length=1)
    name: str
    kind: NodeKind

    # Optional, kind-specific properties bagged here. Validated in subclasses
    # when stricter typing is needed for downstream consumers.
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def _id_format(cls, v: str) -> str:
        if " " in v or any(c.isupper() for c in v):
            raise ValueError(f"Node id must be lowercase, no spaces: got {v!r}")
        return v


class Edge(BaseModel):
    """A directed edge with a typed relationship."""

    source: str
    target: str
    kind: EdgeKind
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


class CountryProperties(BaseModel):
    """Validated property bag for Country nodes."""

    iso_code: str | None = None
    foreign_born_us: int | None = None        # absolute count in U.S.
    immigrant_share: float | None = None      # share of total foreign-born
    top_destination_state: str | None = None
    era: str | None = None                    # 'historic' | 'cold-war' | 'modern'
    gdp_per_capita: float | None = None
    emigration_rate: float | None = None
    conflict_score: float | None = None       # 0-1, optional


class VisaProperties(BaseModel):
    annual_cap: int | None = None
    statutory_authority: str | None = None
    year_established: int | None = None
    top_country: str | None = None


class LawProperties(BaseModel):
    year_enacted: int
    year_repealed: int | None = None
    sponsoring_admin: str | None = None
    full_text_url: str | None = None
    # Stance scores, populated by the stance classifier (Phase 3)
    stance_restrictiveness: float | None = None
    stance_enforcement: float | None = None
    stance_legalization: float | None = None
    stance_humanitarian: float | None = None


class IndustryProperties(BaseModel):
    total_employment: int | None = None
    immigrant_share: float | None = None
    unauthorized_share: float | None = None
    top_origin_corridors: list[str] = Field(default_factory=list)


class LegislatorProperties(BaseModel):
    """Validated property bag for legislator nodes (Phase B)."""

    bioguide_id: str | None = None        # canonical Library of Congress ID
    icpsr_id: int | None = None           # Voteview/ICPSR identifier
    chamber: str | None = None            # 'house' | 'senate'
    party: str | None = None              # 'D' | 'R' | 'I' | other
    state: str | None = None              # USPS code
    first_term: int | None = None
    last_term: int | None = None
    dw_nominate_dim1: float | None = None  # economic / liberal-conservative
    dw_nominate_dim2: float | None = None  # social / regional


class PartyPlatformProperties(BaseModel):
    """Validated property bag for party-platform nodes (Phase B)."""

    party: str                              # 'democratic' | 'republican' | other
    election_year: int
    full_text_url: str | None = None
    immigration_section_text: str | None = None
    cmp_code: str | None = None             # Comparative Manifesto Project code


class NewsOrgProperties(BaseModel):
    """Validated property bag for news-org nodes (Phase B)."""

    homepage: str | None = None
    allsides_bias: str | None = None        # left / center-left / center / center-right / right
    founded_year: int | None = None
    medium: str | None = None               # 'print' | 'digital' | 'broadcast'


class DiscourseEventProperties(BaseModel):
    """Validated property bag for discourse-event nodes (Phase B).

    A discourse event is one piece of recorded immigration speech: a floor
    statement, a published op-ed, a tweet, a campaign-rally line. The graph
    edges (said-by, targets, responds-to) carry the relational structure;
    the properties below carry the per-event content and scores.
    """

    speaker_id: str | None = None           # legislator id, news-org id, or 'anon'
    date: str | None = None                 # ISO 8601 (YYYY-MM-DD)
    medium: str | None = None               # 'speech' | 'op-ed' | 'tweet' | etc.
    text_excerpt: str | None = None
    full_text_url: str | None = None
    # Sentiment scores, populated by the discourse model (Phase B)
    sentiment_hostile: float | None = None
    sentiment_welcoming: float | None = None
    sentiment_dehumanizing: float | None = None
    sentiment_assimilationist: float | None = None


class GraphSpec(BaseModel):
    """A complete graph snapshot."""

    nodes: list[Node]
    edges: list[Edge]

    def node_by_id(self, node_id: str) -> Node | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def neighbors(self, node_id: str) -> list[tuple[Edge, Node]]:
        """Return (edge, neighbor) tuples for a given node id."""
        out: list[tuple[Edge, Node]] = []
        for e in self.edges:
            if e.source == node_id:
                if (n := self.node_by_id(e.target)) is not None:
                    out.append((e, n))
            elif e.target == node_id:
                if (n := self.node_by_id(e.source)) is not None:
                    out.append((e, n))
        return out
