"""Bureau of Labor Statistics — foreign-born labor force.

The BLS Public Data API exposes the Current Population Survey foreign-born
tabulations as time series. We pull the headline series for the four
industry categories the project models (technology, healthcare, construction,
agriculture) plus the overall foreign-born employment level.

The headline series have stable IDs:

    LNS17000000     Total foreign-born civilian labor force, 16+
    LNS17000001     Foreign-born employment level
    LNS14000001     Foreign-born unemployment rate

Industry-by-nativity tabulations are not in the LNS series; they ship as the
annual Foreign-Born Workers report (Table A-7). We document the URL pattern and
let the user drop the XLSX into raw/ if they want industry detail.

Output schema:

    bls_foreign_born.parquet
        series_id  (str)
        year       (int)
        period     (str, "M01"..."M12" or "Q01"..."Q04")
        value      (float)
        source     (str, "bls_<series_id>")
"""
from __future__ import annotations

import json
from pathlib import Path

import httpx
import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="BLS ingest")

DEFAULT_SERIES = (
    "LNS17000000",   # Foreign-born civilian labor force
    "LNS17000001",   # Foreign-born employment level
    "LNS14000001",   # Foreign-born unemployment rate
)


# ============================================================
# Fetch
# ============================================================
def fetch_series(
    series_ids: list[str],
    start_year: int,
    end_year: int,
    api_key: str | None,
) -> pd.DataFrame:
    """Fetch one or more series via the BLS v2 timeseries API."""
    settings = get_settings()
    payload: dict = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if api_key:
        payload["registrationkey"] = api_key
    log.info("Fetching BLS series %s (%d-%d)", series_ids, start_year, end_year)
    with httpx.Client(timeout=60.0) as client:
        r = client.post(settings.bls_api_base, json=payload)
        r.raise_for_status()
        body = r.json()

    if body.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API rejected request: {body.get('message')}")

    rows = []
    for series in body["Results"]["series"]:
        sid = series["seriesID"]
        for obs in series.get("data", []):
            try:
                rows.append({
                    "series_id": sid,
                    "year": int(obs["year"]),
                    "period": obs["period"],
                    "value": float(obs["value"]),
                    "source": f"bls_{sid}",
                })
            except (KeyError, ValueError):
                continue
    return pd.DataFrame(rows)


# ============================================================
# Persist
# ============================================================
def write_raw(df: pd.DataFrame, raw_dir: Path) -> Path:
    out_dir = raw_dir / "bls_lfs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "foreign_born.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    (out_dir / "manifest.json").write_text(json.dumps({
        "series": sorted(df["series_id"].unique().tolist()) if not df.empty else [],
        "year_range": [int(df["year"].min()), int(df["year"].max())] if not df.empty else None,
    }, indent=2))
    return out_path


# ============================================================
# CLI
# ============================================================
@app.command()
def fetch(
    series: list[str] = typer.Option(list(DEFAULT_SERIES), "--series"),
    start: int = typer.Option(2010, "--start"),
    end: int = typer.Option(2024, "--end"),
) -> None:
    """Fetch BLS foreign-born series and write to raw/."""
    settings = get_settings()
    settings.ensure_dirs()
    df = fetch_series(series, start, end, settings.bls_api_key)
    if df.empty:
        log.warning("No BLS rows fetched; nothing written.")
        return
    write_raw(df, settings.raw_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
