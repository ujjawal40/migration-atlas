"""Tests for graph build."""
from __future__ import annotations

from migration_atlas.graph.build import NetworkXBackend, build_default


class TestBuild:
    def test_default_graph_loads(self, graph_backend: NetworkXBackend):
        assert graph_backend.n_nodes() > 30
        assert graph_backend.n_edges() > 30

    def test_idempotent(self):
        b1 = build_default()
        b2 = build_default()
        assert b1.n_nodes() == b2.n_nodes()
        assert b1.n_edges() == b2.n_edges()

    def test_no_dangling_edges(self, graph_backend: NetworkXBackend):
        """Every edge endpoint must reference a node that exists."""
        node_ids = set(graph_backend.graph.nodes)
        for u, v in graph_backend.graph.edges():
            assert u in node_ids, f"dangling source: {u}"
            assert v in node_ids, f"dangling target: {v}"

    def test_node_attributes(self, graph_backend: NetworkXBackend):
        node = graph_backend.graph.nodes["mexico"]
        assert node["name"] == "Mexico"
        assert node["kind"] == "country"
        assert node["foreign_born_us"] == 11_400_000
