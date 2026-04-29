"""Comparative Manifesto Project — coded party-platform positions.

The Manifesto Project (manifesto-project.wzb.eu) hand-codes every sentence in
every party manifesto along ~50 policy categories. Two of those categories
are immediately relevant to us:

    per601    "National way of life: positive"     (often anti-immigration)
    per602    "National way of life: negative"     (often pro-immigration)
    per607    "Multiculturalism: positive"
    per608    "Multiculturalism: negative"

We pull the U.S. subset (DNC + RNC platforms back to 1948) and compute a
single-axis "platform stance on immigration" score per (party, election_year)
as `(per602 + per607 - per601 - per608) / total_sentences`.

The Manifesto Project requires registration and ships the data as XLSX/CSV.
The user drops the file at

    data/raw/manifesto/manifesto_us.csv

and this module parses it. We do not auto-fetch because the Manifesto
Project's terms require user-attribution registration.

Output schema:

    party_platforms.parquet
        party              ('democratic' | 'republican' | other)
        election_year      (int)
        n_sentences        (int)
        per601             (int, anti-immigration sentences)
        per602             (int, pro-immigration sentences)
        per607             (int, pro-multiculturalism sentences)
        per608             (int, anti-multiculturalism sentences)
        immigration_score  (float, in [-1, 1])
        source             ('manifesto_project_<vintage>')
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Manifesto Project ingest")

_PARTY_MAP = {
    61320: "democratic",   # CMP party id for the U.S. Democratic Party
    61620: "republican",   # CMP party id for the U.S. Republican Party
}


def parse(csv_path: Path) -> pd.DataFrame:
    """Parse a CMP CSV export filtered to the U.S. parties.

    Expected columns: party, date (YYYYMM), per601, per602, per607, per608,
    total. The CMP export has additional columns we ignore.
    """
    df = pd.read_csv(csv_path)
    df = df[df["party"].isin(_PARTY_MAP)].copy()
    if df.empty:
        log.warning("No U.S. rows found in %s", csv_path)
        return df

    df["party"] = df["party"].map(_PARTY_MAP)
    df["election_year"] = (df["date"].astype(int) // 100).astype(int)

    for col in ("per601", "per602", "per607", "per608", "total"):
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["immigration_score"] = (
        (df["per602"] + df["per607"] - df["per601"] - df["per608"])
        / df["total"].clip(lower=1)
    ).round(4)

    return df[[
        "party", "election_year", "total",
        "per601", "per602", "per607", "per608",
        "immigration_score",
    ]].rename(columns={"total": "n_sentences"})


def write_raw(df: pd.DataFrame, raw_dir: Path, vintage: str) -> Path:
    out_dir = raw_dir / "manifesto"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source=f"manifesto_project_{vintage}")
    out_path = out_dir / "platforms.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d platform rows to %s", len(df), out_path)
    return out_path


@app.command()
def fetch(
    csv: Path = typer.Option(..., "--csv", help="Path to CMP US export CSV"),
    vintage: str = typer.Option("2024", "--vintage"),
) -> None:
    """Parse a manually-downloaded CMP CSV."""
    settings = get_settings()
    settings.ensure_dirs()
    if not csv.exists():
        raise typer.BadParameter(f"{csv} not found")
    df = parse(csv)
    if df.empty:
        log.warning("No rows parsed.")
        return
    write_raw(df, settings.raw_dir, vintage)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
