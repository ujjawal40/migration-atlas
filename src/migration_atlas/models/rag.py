"""Retrieval-augmented generation over immigration economics research.

Pipeline:
    PDF / Markdown / TXT in data/corpus/
        → text extraction (pypdf for PDFs)
        → chunking (recursive character splitter, ~512 tokens)
        → embedding (sentence-transformers/all-MiniLM-L6-v2 by default)
        → ChromaDB persistent index
        → retrieval at query time
        → optional: synthesis via Anthropic Claude API

The synthesis step is optional. Without an API key, this returns ranked passages.
With a key, it returns a cited natural-language answer.

CLI:
    python -m migration_atlas.models.rag index --config configs/rag.yaml
    python -m migration_atlas.models.rag query --q "what is the wage effect of low-skill immigration?"
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
import yaml

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="RAG CLI")


# ============================================================
# Config
# ============================================================
@dataclass
class RagConfig:
    embedder_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64
    corpus_dir: str = "data/corpus"
    index_dir: str = "chroma_db"
    collection_name: str = "immigration_research"
    top_k: int = 5
    synthesis_model: str = "claude-opus-4-7"
    use_synthesis: bool = False

    @classmethod
    def from_yaml(cls, path: Path | str) -> "RagConfig":
        with open(path) as f:
            return cls(**yaml.safe_load(f))


# ============================================================
# Loading & chunking
# ============================================================
def load_documents(corpus_dir: Path) -> list[dict[str, Any]]:
    """Walk corpus_dir and return [{text, source, page} ...] records."""
    docs: list[dict[str, Any]] = []
    for path in sorted(corpus_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            docs.extend(_load_pdf(path))
        elif suffix in {".md", ".txt"}:
            docs.append({
                "text": path.read_text(encoding="utf-8", errors="ignore"),
                "source": path.name,
                "page": None,
            })
    log.info("Loaded %d document chunks from %s", len(docs), corpus_dir)
    return docs


def _load_pdf(path: Path) -> list[dict[str, Any]]:
    """Extract text from a PDF, page by page."""
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError("pip install pypdf") from e
    reader = PdfReader(str(path))
    out = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            out.append({"text": text, "source": path.name, "page": i + 1})
    return out


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Simple recursive character splitter; preserves rough sentence boundaries."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to break on sentence boundary if we're not at the end
        if end < len(text):
            for delim in [". ", "\n\n", "\n", " "]:
                pos = text.rfind(delim, start, end)
                if pos > start + chunk_size // 2:
                    end = pos + len(delim)
                    break
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]


# ============================================================
# Indexing
# ============================================================
def build_index(cfg: RagConfig) -> None:
    """Build the Chroma index from the corpus directory."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError as e:
        raise ImportError("pip install chromadb") from e

    settings = get_settings()
    corpus_dir = Path(cfg.corpus_dir)
    if not corpus_dir.exists():
        log.warning("Corpus dir %s missing — creating it. Add papers and re-run.", corpus_dir)
        corpus_dir.mkdir(parents=True, exist_ok=True)
        return

    docs = load_documents(corpus_dir)
    if not docs:
        log.warning("No documents found. Add PDFs/MD/TXT to %s", corpus_dir)
        return

    # Chunk
    chunks: list[dict[str, Any]] = []
    for d in docs:
        for j, c in enumerate(chunk_text(d["text"], cfg.chunk_size, cfg.chunk_overlap)):
            chunks.append({
                "text": c,
                "source": d["source"],
                "page": d.get("page"),
                "chunk_id": f"{d['source']}::{d.get('page', 0)}::{j}",
            })
    log.info("Total chunks to index: %d", len(chunks))

    # Index
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=cfg.embedder_model
    )
    client = chromadb.PersistentClient(path=cfg.index_dir)
    # Drop and recreate to avoid stale entries
    try:
        client.delete_collection(cfg.collection_name)
    except Exception:
        pass
    coll = client.create_collection(cfg.collection_name, embedding_function=embedder)

    coll.add(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "page": c["page"] or -1} for c in chunks],
    )
    log.info("Index built. Persisted to %s", cfg.index_dir)


# ============================================================
# Querying
# ============================================================
def retrieve(query: str, cfg: RagConfig, k: int | None = None) -> list[dict[str, Any]]:
    """Retrieve top-k chunks matching the query."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError as e:
        raise ImportError("pip install chromadb") from e

    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=cfg.embedder_model
    )
    client = chromadb.PersistentClient(path=cfg.index_dir)
    coll = client.get_collection(cfg.collection_name, embedding_function=embedder)
    res = coll.query(query_texts=[query], n_results=k or cfg.top_k)

    hits: list[dict[str, Any]] = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "source": meta.get("source"),
                     "page": meta.get("page"), "distance": float(dist)})
    return hits


def synthesize(query: str, hits: list[dict[str, Any]], cfg: RagConfig) -> str:
    """Generate a cited natural-language answer using Claude.

    Falls back to returning the hits as bullets if no API key is set.
    """
    settings = get_settings()
    if not settings.anthropic_api_key or not cfg.use_synthesis:
        return _format_hits_fallback(hits)

    try:
        import anthropic
    except ImportError:
        log.warning("anthropic package not installed; using fallback")
        return _format_hits_fallback(hits)

    context = "\n\n".join(
        f"[{i+1}] (from {h['source']}, page {h['page']}):\n{h['text']}"
        for i, h in enumerate(hits)
    )
    system = (
        "You are a research assistant for a U.S. immigration knowledge graph. "
        "Answer the user's question using ONLY the supplied passages. "
        "Cite sources using bracket notation: [1], [2], etc. "
        "If the passages do not contain the answer, say so honestly."
    )
    user = f"Question: {query}\n\nPassages:\n{context}\n\nAnswer:"

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model=cfg.synthesis_model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def _format_hits_fallback(hits: list[dict[str, Any]]) -> str:
    """Format hits as a bulleted answer when synthesis is unavailable."""
    if not hits:
        return "No relevant passages found in the corpus."
    lines = ["Top retrieved passages (synthesis disabled):", ""]
    for i, h in enumerate(hits, 1):
        snippet = h["text"][:300] + ("..." if len(h["text"]) > 300 else "")
        lines.append(f"[{i}] {h['source']} (page {h['page']}, distance={h['distance']:.3f})")
        lines.append(f"    {snippet}")
        lines.append("")
    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================
@app.command()
def index(config: Path = typer.Option("configs/rag.yaml", "--config", "-c")) -> None:
    """Build the vector index from the corpus directory."""
    cfg = RagConfig.from_yaml(config)
    build_index(cfg)


@app.command()
def query(
    q: str = typer.Option(..., "--q", help="Question text"),
    config: Path = typer.Option("configs/rag.yaml", "--config", "-c"),
    k: int = typer.Option(5, "--k"),
) -> None:
    """Query the index and synthesize an answer."""
    cfg = RagConfig.from_yaml(config)
    hits = retrieve(q, cfg, k=k)
    answer = synthesize(q, hits, cfg)
    print(answer)
    print("\n---\nSources:")
    for h in hits:
        print(f"  - {h['source']} (page {h['page']}, distance={h['distance']:.3f})")


if __name__ == "__main__":
    app()
