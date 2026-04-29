"""Ingest the research-paper corpus into a parquet of pre-chunked text.

Used by the RAG indexer in `migration_atlas.models.rag`. Separated from the
indexer so chunking can be re-run independently of embedding.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.models.rag import chunk_text, load_documents
from migration_atlas.utils import get_logger

log = get_logger(__name__)
app = typer.Typer(help="Corpus ingestion CLI")


@app.command()
def run(
    src: Path = typer.Option(Path("data/corpus"), "--src"),
    out: Path = typer.Option(Path("data/processed/chunks.parquet"), "--out"),
    chunk_size: int = typer.Option(512, "--chunk-size"),
    overlap: int = typer.Option(64, "--overlap"),
) -> None:
    """Walk src/, chunk every supported document, write parquet to out."""
    docs = load_documents(src)
    rows = []
    for d in docs:
        for j, c in enumerate(chunk_text(d["text"], chunk_size, overlap)):
            rows.append({
                "text": c,
                "source": d["source"],
                "page": d.get("page"),
                "chunk_index": j,
            })
    if not rows:
        log.warning("No chunks produced. Add documents to %s and re-run.", src)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(out, index=False)
    log.info("Wrote %d chunks to %s", len(rows), out)


if __name__ == "__main__":
    app()
