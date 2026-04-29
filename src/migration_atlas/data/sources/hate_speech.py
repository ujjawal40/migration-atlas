"""Hate-speech corpora for the discourse classifier (Phase B).

Three published datasets, all available via HuggingFace Datasets, are loaded
into a unified labeled corpus that the sentiment / hate-speech classifier
fine-tunes on:

    HateXplain (Mathew et al. 2021)         hatexplain
        Twitter + Gab posts. 3-way label (hate / offensive / normal) plus
        per-token rationales.

    Davidson et al. 2017                    tdavidson/hate_speech_offensive
        Twitter posts. 3-way label (hate / offensive / neither).

    Founta et al. 2018                      not yet on HF; manual download
        Twitter posts. 4-way label (hateful / abusive / spam / normal).
        Drop CSV at data/raw/hate_speech/founta.csv.

We harmonize all three to a single 4-class taxonomy:

    label ∈ {'hateful', 'offensive', 'normal', 'spam'}

Output schema:

    discourse_labels.parquet
        text       (str)
        label      (str, one of the four classes)
        target     (str, optional — 'immigrant' / 'racial' / 'gender' / etc.)
        source     (str, 'hatexplain' | 'davidson' | 'founta')
        split      (str, 'train' | 'val' | 'test')
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Hate-speech corpora ingest")


def load_hatexplain() -> pd.DataFrame:
    """Load HateXplain via HuggingFace Datasets."""
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise ImportError("pip install datasets") from e

    log.info("Loading HateXplain from HuggingFace Datasets")
    ds = load_dataset("hatexplain")
    rows = []
    for split in ("train", "validation", "test"):
        if split not in ds:
            continue
        for row in ds[split]:
            # HateXplain stores three annotator labels per row; majority vote.
            labels = row["annotators"]["label"]
            from collections import Counter
            top = Counter(labels).most_common(1)[0][0]
            label = ["hateful", "normal", "offensive"][top]
            target = (row["annotators"]["target"] or [[]])[0]
            target_str = target[0] if target else None
            rows.append({
                "text": " ".join(row["post_tokens"]),
                "label": label,
                "target": target_str,
                "source": "hatexplain",
                "split": "val" if split == "validation" else split,
            })
    return pd.DataFrame(rows)


def load_davidson() -> pd.DataFrame:
    """Load Davidson 2017 hate-speech dataset."""
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise ImportError("pip install datasets") from e

    log.info("Loading Davidson hate_speech_offensive")
    ds = load_dataset("tdavidson/hate_speech_offensive")
    label_map = {0: "hateful", 1: "offensive", 2: "normal"}
    rows = []
    for split, frame in ds.items():
        for row in frame:
            rows.append({
                "text": row["tweet"],
                "label": label_map.get(row["class"], "normal"),
                "target": None,
                "source": "davidson",
                "split": split,
            })
    return pd.DataFrame(rows)


def load_founta(csv_path: Path) -> pd.DataFrame:
    """Load Founta from a manually-placed CSV.

    Expected columns: tweet_id, text, label (hateful|abusive|spam|normal).
    """
    if not csv_path.exists():
        log.warning("Founta CSV not found at %s; skipping", csv_path)
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    df = df.assign(target=None, source="founta", split="train")
    return df[["text", "label", "target", "source", "split"]]


def write_raw(df: pd.DataFrame, raw_dir: Path) -> Path:
    out_dir = raw_dir / "hate_speech"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "labels.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d labeled examples to %s", len(df), out_path)
    log.info("Per-source counts: %s", df["source"].value_counts().to_dict())
    return out_path


@app.command()
def fetch(
    skip_founta: bool = typer.Option(False, "--skip-founta"),
) -> None:
    """Load HateXplain + Davidson (and Founta if CSV is present)."""
    settings = get_settings()
    settings.ensure_dirs()
    frames = [load_hatexplain(), load_davidson()]
    if not skip_founta:
        frames.append(load_founta(settings.raw_dir / "hate_speech" / "founta.csv"))
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    if combined.empty:
        log.warning("No labeled examples loaded.")
        return
    write_raw(combined, settings.raw_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
