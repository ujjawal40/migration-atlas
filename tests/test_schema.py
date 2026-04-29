"""Tests for the graph schema."""
from __future__ import annotations

import pytest

from migration_atlas.graph.schema import (
    Edge, EdgeKind, GraphSpec, Node, NodeKind,
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
