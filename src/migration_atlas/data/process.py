"""Harmonize raw source outputs into the canonical processed schema.

Every consumer downstream (graph builder, forecaster, frontend) reads from
`data/processed/`. Sources land in `data/raw/`; this module is the single
boundary between the two.

Canonical output files:

    foreign_born_by_country.parquet     (year, country, count, moe)
    visa_issuance.parquet               (year, country, flow)
    flows.parquet                       (year, country, flow)        ← forecaster input
    labor_force.parquet                 (year, period, series_id, value)
    unauthorized.parquet                (year, country, unauth_pop)
    profiles.parquet                    (year, country, metric, value)

The flows series the forecaster trains on is a derived view: where USCIS
Yearbook data is available we use it directly (legal flow); where not, we fall
back to year-over-year ACS deltas in foreign-born stock as a flow proxy.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Data processing CLI")


# ============================================================
# Per-output processors
# ============================================================
def process_foreign_born(raw_dir: Path, processed_dir: Path) -> Path | None:
    """Pass-through Census ACS B05006 with a sort + dedupe."""
    src = raw_dir / "census_acs" / "foreign_born.parquet"
    if not src.exists():
        log.info("Skipping foreign_born: %s missing", src)
        return None
    df = pd.read_parquet(src)
    df = df.drop_duplicates(["country", "year"]).sort_values(["country", "year"])
    out = processed_dir / "foreign_born_by_country.parquet"
    df.to_parquet(out, index=False)
    log.info("Wrote foreign_born_by_country.parquet (%d rows)", len(df))
    return out


def process_visa_issuance(raw_dir: Path, processed_dir: Path) -> Path | None:
    """Pass-through USCIS Yearbook Table 3 with sort + dedupe."""
    src = raw_dir / "uscis_yearbook" / "visa_issuance.parquet"
    if not src.exists():
        log.info("Skipping visa_issuance: %s missing", src)
        return None
    df = pd.read_parquet(src)
    df = df.drop_duplicates(["country", "year"]).sort_values(["country", "year"])
    out = processed_dir / "visa_issuance.parquet"
    df.to_parquet(out, index=False)
    log.info("Wrote visa_issuance.parquet (%d rows)", len(df))
    return out


def process_flows(raw_dir: Path, processed_dir: Path) -> Path | None:
    """Build the forecaster's flow series.

    Preference order, per (country, year):
        1. USCIS Yearbook flow if present (legal flow, gold-standard)
        2. ACS year-over-year stock delta if both vintages present (proxy)
        3. Skip
    """
    yearbook_path = raw_dir / "uscis_yearbook" / "visa_issuance.parquet"
    acs_path = raw_dir / "census_acs" / "foreign_born.parquet"

    frames: list[pd.DataFrame] = []

    if yearbook_path.exists():
        yb = pd.read_parquet(yearbook_path)
        yb = yb[["country", "year", "flow"]].assign(method="uscis_yearbook")
        frames.append(yb)

    if acs_path.exists():
        acs = pd.read_parquet(acs_path).sort_values(["country", "year"])
        acs["flow"] = acs.groupby("country")["count"].diff().clip(lower=0)
        proxy = (
            acs.dropna(subset=["flow"])
            .assign(flow=lambda d: d["flow"].astype(int), method="acs_stock_delta")
            [["country", "year", "flow", "method"]]
        )
        frames.append(proxy)

    if not frames:
        log.warning("No flow source available; flows.parquet not written.")
        return None

    combined = pd.concat(frames, ignore_index=True)
    # Yearbook wins per (country, year).
    method_priority = {"uscis_yearbook": 0, "acs_stock_delta": 1}
    combined["_pri"] = combined["method"].map(method_priority)
    combined = (
        combined.sort_values(["country", "year", "_pri"])
        .drop_duplicates(["country", "year"], keep="first")
        .drop(columns=["_pri"])
        .sort_values(["country", "year"])
    )
    out = processed_dir / "flows.parquet"
    combined.to_parquet(out, index=False)
    log.info(
        "Wrote flows.parquet (%d rows, %s)",
        len(combined),
        combined["method"].value_counts().to_dict(),
    )
    return out


def process_labor_force(raw_dir: Path, processed_dir: Path) -> Path | None:
    src = raw_dir / "bls_lfs" / "foreign_born.parquet"
    if not src.exists():
        log.info("Skipping labor_force: %s missing", src)
        return None
    df = pd.read_parquet(src)
    out = processed_dir / "labor_force.parquet"
    df.to_parquet(out, index=False)
    log.info("Wrote labor_force.parquet (%d rows)", len(df))
    return out


def process_unauthorized(raw_dir: Path, processed_dir: Path) -> Path | None:
    src = raw_dir / "pew" / "unauthorized.parquet"
    if not src.exists():
        log.info("Skipping unauthorized: %s missing", src)
        return None
    df = pd.read_parquet(src)
    out = processed_dir / "unauthorized.parquet"
    df.to_parquet(out, index=False)
    log.info("Wrote unauthorized.parquet (%d rows)", len(df))
    return out


def process_profiles(raw_dir: Path, processed_dir: Path) -> Path | None:
    src = raw_dir / "mpi" / "profiles.parquet"
    if not src.exists():
        log.info("Skipping profiles: %s missing", src)
        return None
    df = pd.read_parquet(src)
    out = processed_dir / "profiles.parquet"
    df.to_parquet(out, index=False)
    log.info("Wrote profiles.parquet (%d rows)", len(df))
    return out


# ============================================================
# Orchestration
# ============================================================
@app.command()
def all() -> None:
    """Process all available raw outputs into the canonical processed schema."""
    settings = get_settings()
    settings.ensure_dirs()
    raw, proc = settings.raw_dir, settings.processed_dir
    proc.mkdir(parents=True, exist_ok=True)

    process_foreign_born(raw, proc)
    process_visa_issuance(raw, proc)
    process_flows(raw, proc)
    process_labor_force(raw, proc)
    process_unauthorized(raw, proc)
    process_profiles(raw, proc)

    written = sorted(p.name for p in proc.glob("*.parquet"))
    log.info("Processed outputs: %s", written)


@app.command()
def flows() -> None:
    """Build only the flows.parquet (the forecaster's input)."""
    settings = get_settings()
    settings.ensure_dirs()
    process_flows(settings.raw_dir, settings.processed_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
