"""Tests for the graph schema."""
from __future__ import annotations

import pytest

from migration_atlas.graph.schema import (
    DiscourseEventProperties,
    Edge,
    EdgeKind,
    GraphSpec,
    LegislatorProperties,
    NewsOrgProperties,
    Node,
    NodeKind,
    PartyPlatformProperties,
)


class TestNode:
    def test_valid_node(self):
        n = Node(id="mexico", name="Mexico", kind=NodeKind.COUNTRY)
        assert n.id == "mexico"
        assert n.kind == NodeKind.COUNTRY

    def test_id_must_be_lowercase(self):
        with pytest.raises(ValueError, match="lowercase"):
            Node(id="Mexico", name="Mexico", kind=NodeKind.COUNTRY)

    def test_id_no_spaces(self):
        with pytest.raises(ValueError, match="lowercase"):
            Node(id="united kingdom", name="UK", kind=NodeKind.COUNTRY)

    def test_properties_default_to_empty(self):
        n = Node(id="x", name="X", kind=NodeKind.COUNTRY)
        assert n.properties == {}


class TestEdge:
    def test_valid_edge(self):
        e = Edge(source="india", target="h-1b", kind=EdgeKind.USES_VISA)
        assert e.weight == 1.0

    def test_weight_can_be_set(self):
        e = Edge(source="india", target="h-1b", kind=EdgeKind.USES_VISA, weight=0.7)
        assert e.weight == 0.7


class TestGraphSpec:
    def test_node_lookup(self, graph_spec: GraphSpec):
        n = graph_spec.node_by_id("india")
        assert n is not None
        assert n.name == "India"

    def test_node_lookup_missing(self, graph_spec: GraphSpec):
        assert graph_spec.node_by_id("atlantis") is None

    def test_neighbors(self, graph_spec: GraphSpec):
        neighbors = graph_spec.neighbors("india")
        assert len(neighbors) > 0
        # India should be connected to H-1B
        ids = [n.id for _, n in neighbors]
        assert "h-1b" in ids


class TestPhaseBKinds:
    """Phase B introduces four new node kinds and four new edge kinds."""

    def test_party_platform_kind_exists(self):
        assert NodeKind.PARTY_PLATFORM.value == "party-platform"

    def test_legislator_kind_exists(self):
        assert NodeKind.LEGISLATOR.value == "legislator"

    def test_news_org_kind_exists(self):
        assert NodeKind.NEWS_ORG.value == "news-org"

    def test_discourse_event_kind_exists(self):
        assert NodeKind.DISCOURSE_EVENT.value == "discourse-event"

    def test_said_by_edge_kind(self):
        assert EdgeKind.SAID_BY.value == "said-by"

    def test_affiliated_with_edge_kind(self):
        assert EdgeKind.AFFILIATED_WITH.value == "affiliated-with"

    def test_targets_edge_kind(self):
        assert EdgeKind.TARGETS.value == "targets"

    def test_responds_to_edge_kind(self):
        assert EdgeKind.RESPONDS_TO.value == "responds-to"


class TestLegislatorProperties:
    def test_minimum_valid(self):
        p = LegislatorProperties(party="D", state="CA")
        assert p.party == "D"
        assert p.dw_nominate_dim1 is None

    def test_dw_nominate_optional(self):
        p = LegislatorProperties(dw_nominate_dim1=-0.45, dw_nominate_dim2=0.12)
        assert p.dw_nominate_dim1 == -0.45


class TestPartyPlatformProperties:
    def test_required_fields(self):
        p = PartyPlatformProperties(party="democratic", election_year=2024)
        assert p.party == "democratic"
        assert p.election_year == 2024

    def test_election_year_required(self):
        with pytest.raises(ValueError):
            PartyPlatformProperties(party="democratic")  # type: ignore[call-arg]


class TestNewsOrgProperties:
    def test_optional_fields(self):
        p = NewsOrgProperties(homepage="https://example.org", allsides_bias="center")
        assert p.allsides_bias == "center"


class TestDiscourseEventProperties:
    def test_sentiment_axes_optional(self):
        p = DiscourseEventProperties(speaker_id="legis_42")
        assert p.sentiment_hostile is None

    def test_sentiment_axes_settable(self):
        p = DiscourseEventProperties(
            sentiment_hostile=0.3,
            sentiment_welcoming=0.4,
            sentiment_dehumanizing=0.1,
            sentiment_assimilationist=0.6,
        )
        assert p.sentiment_hostile == 0.3
