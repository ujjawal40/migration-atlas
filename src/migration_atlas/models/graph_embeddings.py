"""Graph embeddings via Node2Vec.

Trains a Node2Vec model on the knowledge graph and exposes two capabilities:

    1. Similarity — `most_similar('mexico')` returns countries / visas whose
       neighborhoods most resemble Mexico's.

    2. Link prediction — given two nodes that aren't connected, score the
       likelihood that an edge between them is plausible. Useful for surfacing
       gaps in the seed data.

CLI:
    python -m migration_atlas.models.graph_embeddings train --config configs/embeddings.yaml
    python -m migration_atlas.models.graph_embeddings similar --node mexico --top-k 10
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import typer
import yaml

from migration_atlas.graph.build import build_default
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Graph embeddings CLI")


@dataclass
class EmbeddingsConfig:
    dimensions: int = 64
    walk_length: int = 16
    num_walks: int = 100
    p: float = 1.0  # return parameter
    q: float = 1.0  # in-out parameter
    window: int = 5
    min_count: int = 1
    workers: int = 2
    seed: int = 42
    output_path: str = "checkpoints/node2vec.kv"

    @classmethod
    def from_yaml(cls, path: Path | str) -> "EmbeddingsConfig":
        with open(path) as f:
            return cls(**yaml.safe_load(f))


def train_embeddings(cfg: EmbeddingsConfig) -> None:
    """Fit Node2Vec on the seed graph and save the embeddings."""
    try:
        from node2vec import Node2Vec
    except ImportError as e:
        raise ImportError("pip install node2vec") from e

    backend = build_default()
    # Node2Vec wants a simple (Multi)Graph; convert directed to undirected for walks
    g = backend.graph.to_undirected()

    log.info("Training Node2Vec on %d nodes / %d edges (dim=%d)",
             g.number_of_nodes(), g.number_of_edges(), cfg.dimensions)

    n2v = Node2Vec(
        g,
        dimensions=cfg.dimensions,
        walk_length=cfg.walk_length,
        num_walks=cfg.num_walks,
        p=cfg.p,
        q=cfg.q,
        workers=cfg.workers,
        seed=cfg.seed,
        quiet=True,
    )
    model = n2v.fit(window=cfg.window, min_count=cfg.min_count, seed=cfg.seed)

    out_path = Path(cfg.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    model.wv.save(str(out_path))
    (out_path.parent / "embeddings_config.json").write_text(json.dumps(cfg.__dict__, indent=2))
    log.info("Saved embeddings to %s", out_path)


def load_embeddings(path: Path | str):
    """Load saved Node2Vec embeddings."""
    from gensim.models import KeyedVectors
    return KeyedVectors.load(str(path))


def most_similar(node_id: str, top_k: int = 10, kv=None) -> list[tuple[str, float]]:
    """Return the top-k most similar nodes by cosine similarity."""
    if kv is None:
        settings = get_settings()
        kv = load_embeddings(settings.embeddings_path)
    if node_id not in kv.key_to_index:
        raise KeyError(f"Node {node_id!r} not in embedding vocabulary")
    return [(k, float(s)) for k, s in kv.most_similar(node_id, topn=top_k)]


def link_score(source: str, target: str, kv=None) -> float:
    """Cosine similarity as a proxy for link plausibility."""
    if kv is None:
        settings = get_settings()
        kv = load_embeddings(settings.embeddings_path)
    return float(kv.similarity(source, target))


# ============================================================
# CLI
# ============================================================
@app.command()
def train(config: Path = typer.Option("configs/embeddings.yaml", "--config", "-c")) -> None:
    """Fit Node2Vec on the knowledge graph."""
    cfg = EmbeddingsConfig.from_yaml(config)
    train_embeddings(cfg)


@app.command()
def similar(
    node: str = typer.Option(..., "--node"),
    top_k: int = typer.Option(10, "--top-k"),
) -> None:
    """Print most-similar nodes."""
    results = most_similar(node, top_k)
    print(f"\nMost similar to {node!r}:\n")
    for n, s in results:
        print(f"  {s:.3f}  {n}")


@app.command(name="link-score")
def link_score_cmd(
    source: str = typer.Option(..., "--source"),
    target: str = typer.Option(..., "--target"),
) -> None:
    """Score the plausibility of an edge between two nodes."""
    s = link_score(source, target)
    print(f"\nlink_score({source!r}, {target!r}) = {s:.3f}\n")


if __name__ == "__main__":
    app()
