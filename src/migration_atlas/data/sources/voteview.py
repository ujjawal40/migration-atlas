"""Voteview / DW-NOMINATE — legislator metadata.

Voteview (voteview.com, Lewis et al.) publishes the canonical roll-call data
for the U.S. Congress along with DW-NOMINATE ideal-point estimates for every
legislator since the 1st Congress. We pull the all-Congress members file and
filter to the relevant Congresses for our discourse corpus.

The HSall_members.csv file is publicly downloadable, no key required.

Output schema:

    legislators.parquet
        bioguide_id      (str)
        icpsr_id         (int)
        chamber          ('house' | 'senate')
        party            (str, e.g. 'D', 'R', 'I')
        state            (str, USPS code)
        congress         (int)
        first_term       (int, calendar year)
        last_term        (int, calendar year)
        dw_nominate_dim1 (float)
        dw_nominate_dim2 (float)
        source           ('voteview_<download_year>')
"""
from __future__ import annotations

from pathlib import Path

import httpx
import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Voteview ingest")

VOTEVIEW_MEMBERS_URL = "https://voteview.com/static/data/out/members/HSall_members.csv"

# Map Voteview's chamber enum to our string values.
_CHAMBER_MAP = {"House": "house", "Senate": "senate"}

# Congress N spans years (1789 + (N-1)*2) through (1789 + N*2).
def _congress_to_years(congress: int) -> tuple[int, int]:
    start = 1789 + (congress - 1) * 2
    return (start, start + 2)


def download(url: str, dest: Path, force: bool = False) -> Path:
    if dest.exists() and not force:
        log.info("Using cached Voteview members at %s", dest)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.info("Downloading Voteview members file: %s", url)
    with httpx.Client(
        headers={"User-Agent": "migration-atlas/0.1"},
        follow_redirects=True,
        timeout=120.0,
    ) as client:
        r = client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)
    log.info("Saved %d bytes to %s", len(r.content), dest)
    return dest


def parse(csv_path: Path, min_congress: int = 89) -> pd.DataFrame:
    """Parse the Voteview HSall_members.csv into our canonical schema.

    Default min_congress=89 = the 89th Congress (1965-1967), which covers
    the post-INA era our discourse corpus will focus on. Earlier Congresses
    are available but currently out of scope.
    """
    df = pd.read_csv(csv_path)
    df = df[df["congress"] >= min_congress].copy()

    # Normalize columns
    df["chamber"] = df["chamber"].map(_CHAMBER_MAP)
    df = df.dropna(subset=["chamber"])

    rows = []
    for _, r in df.iterrows():
        first_year, last_year = _congress_to_years(int(r["congress"]))
        rows.append({
            "bioguide_id": r.get("bioguide_id"),
            "icpsr_id": int(r["icpsr"]) if pd.notna(r.get("icpsr")) else None,
            "chamber": r["chamber"],
            "party": _party_from_code(r.get("party_code")),
            "state": r.get("state_abbrev"),
            "congress": int(r["congress"]),
            "first_term": first_year,
            "last_term": last_year,
            "dw_nominate_dim1": _float(r.get("nominate_dim1")),
            "dw_nominate_dim2": _float(r.get("nominate_dim2")),
        })
    return pd.DataFrame(rows)


def _float(v) -> float | None:
    try:
        f = float(v)
        return f if f == f else None  # NaN check
    except (TypeError, ValueError):
        return None


def _party_from_code(code) -> str | None:
    """Voteview's numeric party codes mapped to single-letter symbols.

    100 = Democrat, 200 = Republican, 328 = Independent. Other historical
    codes (e.g. Whig, Free Soil) are not relevant for the post-1965 window.
    """
    try:
        c = int(code)
    except (TypeError, ValueError):
        return None
    return {100: "D", 200: "R", 328: "I"}.get(c)


def write_raw(df: pd.DataFrame, raw_dir: Path, vintage_tag: str) -> Path:
    out_dir = raw_dir / "voteview"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source=f"voteview_{vintage_tag}")
    out_path = out_dir / "legislators.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    return out_path


@app.command()
def fetch(
    url: str = typer.Option(VOTEVIEW_MEMBERS_URL, "--url"),
    min_congress: int = typer.Option(89, "--min-congress"),
    vintage_tag: str = typer.Option("2024", "--vintage"),
) -> None:
    """Fetch the Voteview members file and write to raw/."""
    settings = get_settings()
    settings.ensure_dirs()
    csv_path = download(
        url, settings.raw_dir / "voteview" / f"members_{vintage_tag}.csv"
    )
    df = parse(csv_path, min_congress=min_congress)
    if df.empty:
        log.warning("No rows parsed.")
        return
    write_raw(df, settings.raw_dir, vintage_tag)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
