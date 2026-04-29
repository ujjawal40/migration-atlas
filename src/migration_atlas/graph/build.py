"""Build the knowledge graph from seed data (and later, from ETL outputs).

Two backends supported:
- NetworkX (default, in-memory, no infra required)
- Neo4j (production, persistent, supports Cypher)

Both produce equivalent semantic content; tests assert this.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import networkx as nx

from migration_atlas.graph.schema import Edge, GraphSpec, Node
from migration_atlas.graph.seed import all_edges, all_nodes
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)


class GraphBackend(Protocol):
    """Common interface for both NetworkX and Neo4j backends."""

    def add_node(self, node: Node) -> None: ...
    def add_edge(self, edge: Edge) -> None: ...
    def n_nodes(self) -> int: ...
    def n_edges(self) -> int: ...


# ============================================================
# NetworkX backend
# ============================================================
class NetworkXBackend:
    """In-memory graph backed by networkx.MultiDiGraph."""

    def __init__(self) -> None:
        self.graph: nx.MultiDiGraph = nx.MultiDiGraph()

    def add_node(self, node: Node) -> None:
        self.graph.add_node(
            node.id,
            name=node.name,
            kind=node.kind.value,
            **node.properties,
        )

    def add_edge(self, edge: Edge) -> None:
        self.graph.add_edge(
            edge.source,
            edge.target,
            key=edge.kind.value,
            kind=edge.kind.value,
            weight=edge.weight,
            **edge.properties,
        )

    def n_nodes(self) -> int:
        return self.graph.number_of_nodes()

    def n_edges(self) -> int:
        return self.graph.number_of_edges()


# ============================================================
# Neo4j backend (optional — only if neo4j extra is installed)
# ============================================================
class Neo4jBackend:
    """Persistent graph in a running Neo4j instance."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as e:
            raise ImportError(
                "Install with: pip install -e '.[neo4j]'"
            ) from e
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._counts = {"nodes": 0, "edges": 0}

    def add_node(self, node: Node) -> None:
        kind_label = node.kind.value.title().replace("-", "")
        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:{kind_label} {{id: $id}})
                SET n.name = $name, n += $props
                """,
                id=node.id, name=node.name, props=node.properties,
            )
        self._counts["nodes"] += 1

    def add_edge(self, edge: Edge) -> None:
        rel_type = edge.kind.value.upper().replace("-", "_")
        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (s {{id: $src}}), (t {{id: $tgt}})
                MERGE (s)-[r:{rel_type}]->(t)
                SET r.weight = $weight, r += $props
                """,
                src=edge.source, tgt=edge.target,
                weight=edge.weight, props=edge.properties,
            )
        self._counts["edges"] += 1

    def n_nodes(self) -> int:
        return self._counts["nodes"]

    def n_edges(self) -> int:
        return self._counts["edges"]

    def close(self) -> None:
        self.driver.close()


# ============================================================
# Build orchestration
# ============================================================
def build_graph(backend: GraphBackend, nodes: list[Node], edges: list[Edge]) -> GraphBackend:
    """Populate the given backend with the given nodes and edges."""
    log.info("Adding %d nodes...", len(nodes))
    for n in nodes:
        backend.add_node(n)
    log.info("Adding %d edges...", len(edges))
    for e in edges:
        backend.add_edge(e)
    log.info("Done. Graph has %d nodes, %d edges.", backend.n_nodes(), backend.n_edges())
    return backend


def build_default() -> NetworkXBackend:
    """Build the default seed graph in NetworkX."""
    backend = NetworkXBackend()
    build_graph(backend, all_nodes(), all_edges())
    return backend


def export_to_json(graph: nx.MultiDiGraph, path: Path) -> None:
    """Export a NetworkX graph to JSON for the frontend."""
    nodes_out = [
        {"id": nid, **dict(graph.nodes[nid])} for nid in graph.nodes
    ]
    edges_out = []
    for u, v, k, attrs in graph.edges(keys=True, data=True):
        edges_out.append({"source": u, "target": v, "kind": k, **attrs})

    payload = {"nodes": nodes_out, "links": edges_out}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))
    log.info("Wrote graph JSON to %s", path)


def main() -> None:
    """Entry point: `python -m migration_atlas.graph.build`"""
    settings = get_settings()
    settings.ensure_dirs()

    log.info("Building knowledge graph (backend=%s)", settings.graph_backend)

    if settings.graph_backend == "networkx":
        backend = build_default()
        export_to_json(backend.graph, settings.processed_dir / "graph.json")
    elif settings.graph_backend == "neo4j":
        backend = Neo4jBackend(
            settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
        )
        try:
            build_graph(backend, all_nodes(), all_edges())
        finally:
            backend.close()
    else:
        raise ValueError(f"Unknown backend: {settings.graph_backend}")


def to_spec() -> GraphSpec:
    """Return the seed graph as a GraphSpec (for testing)."""
    return GraphSpec(nodes=all_nodes(), edges=all_edges())


if __name__ == "__main__":
    main()
