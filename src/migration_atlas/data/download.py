"""Top-level orchestrator for the data layer.

Calls each per-source ingest module in turn, writes raw outputs to
`data/raw/<source>/`, and emits a summary manifest at the end. Failures in any
one source do not block the others; the manifest records which sources
succeeded so `process.py` can decide what to harmonize.

CLI:

    python -m migration_atlas.data.download all                  # everything
    python -m migration_atlas.data.download census --years 2023  # one source
    python -m migration_atlas.data.download uscis
    python -m migration_atlas.data.download list-sources
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import typer

from migration_atlas.data.sources import bls, census_acs, mpi, pew, uscis_yearbook
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Data download CLI")


SOURCES = {
    "census_acs": {
        "description": "American Community Survey, table B05006 (foreign-born by origin)",
        "url": "https://api.census.gov/data/2023/acs/acs1",
        "requires": "CENSUS_API_KEY (free, register at api.census.gov)",
        "license": "Public domain (U.S. government work)",
    },
    "uscis_yearbook": {
        "description": "OHSS Yearbook Table 3 (LPR by country)",
        "url": "https://www.dhs.gov/ohss/topics/immigration/yearbook",
        "requires": "Direct download; URL configurable",
        "license": "Public domain",
    },
    "bls_lfs": {
        "description": "BLS foreign-born labor force series",
        "url": "https://api.bls.gov/publicAPI/v2",
        "requires": "BLS_API_KEY (optional; raises rate limit)",
        "license": "Public domain",
    },
    "pew": {
        "description": "Pew Research unauthorized-population estimates",
        "url": "https://www.pewresearch.org/hispanic/",
        "requires": "Manually drop XLSX into data/raw/pew/",
        "license": "Free for academic use; cite Pew",
    },
    "mpi": {
        "description": "Migration Policy Institute Data Hub tabulations",
        "url": "https://www.migrationpolicy.org/programs/data-hub",
        "requires": "Manually drop XLSX into data/raw/mpi/",
        "license": "Free for non-commercial use; cite MPI",
    },
}


# ============================================================
# Per-source dispatchers
# ============================================================
def _run_census(years: list[int]) -> dict:
    settings = get_settings()
    if not settings.census_api_key:
        return {"status": "skipped", "reason": "CENSUS_API_KEY not set"}
    try:
        df = census_acs.fetch_years(years)
        if df.empty:
            return {"status": "empty"}
        path = census_acs.write_raw(df, settings.raw_dir)
        return {"status": "ok", "rows": len(df), "path": str(path)}
    except Exception as e:
        log.exception("census_acs failed")
        return {"status": "error", "error": str(e)}


def _run_uscis(url: str | None, vintage_tag: str) -> dict:
    settings = get_settings()
    try:
        url = url or settings.uscis_yearbook_url
        xlsx = uscis_yearbook.download(
            url, settings.raw_dir / "uscis_yearbook" / f"yearbook_{vintage_tag}.xlsx"
        )
        long = uscis_yearbook.parse_table3(xlsx)
        canonical = uscis_yearbook.harmonize(long)
        path = uscis_yearbook.write_raw(canonical, settings.raw_dir, vintage_tag)
        return {"status": "ok", "rows": len(canonical), "path": str(path)}
    except Exception as e:
        log.exception("uscis_yearbook failed")
        return {"status": "error", "error": str(e)}


def _run_bls(start: int, end: int) -> dict:
    settings = get_settings()
    try:
        df = bls.fetch_series(list(bls.DEFAULT_SERIES), start, end, settings.bls_api_key)
        if df.empty:
            return {"status": "empty"}
        path = bls.write_raw(df, settings.raw_dir)
        return {"status": "ok", "rows": len(df), "path": str(path)}
    except Exception as e:
        log.exception("bls failed")
        return {"status": "error", "error": str(e)}


def _run_pew_local() -> dict:
    settings = get_settings()
    candidates = list((settings.raw_dir / "pew").glob("*.xlsx"))
    if not candidates:
        return {"status": "skipped", "reason": "No XLSX in data/raw/pew/"}
    try:
        df = pew.parse(candidates[0])
        if df.empty:
            return {"status": "empty"}
        path = pew.write_raw(df, settings.raw_dir, report_year=2024)
        return {"status": "ok", "rows": len(df), "path": str(path)}
    except Exception as e:
        log.exception("pew failed")
        return {"status": "error", "error": str(e)}


def _run_mpi_local() -> dict:
    settings = get_settings()
    candidates = list((settings.raw_dir / "mpi").glob("*.xlsx"))
    if not candidates:
        return {"status": "skipped", "reason": "No XLSX in data/raw/mpi/"}
    try:
        df = mpi.parse(candidates[0])
        if df.empty:
            return {"status": "empty"}
        path = mpi.write_raw(df, settings.raw_dir)
        return {"status": "ok", "rows": len(df), "path": str(path)}
    except Exception as e:
        log.exception("mpi failed")
        return {"status": "error", "error": str(e)}


# ============================================================
# CLI commands
# ============================================================
@app.command(name="list-sources")
def list_sources() -> None:
    """Print the source registry."""
    print(json.dumps(SOURCES, indent=2))


@app.command()
def census(
    years: list[int] = typer.Option(
        [2019, 2020, 2021, 2022, 2023], "--years", "-y"
    ),
) -> None:
    """Fetch Census ACS B05006 across the given vintages."""
    result = _run_census(years)
    print(json.dumps(result, indent=2))


@app.command()
def uscis(
    url: str = typer.Option(None, "--url"),
    vintage_tag: str = typer.Option("2023", "--vintage"),
) -> None:
    """Fetch the USCIS Yearbook XLSX."""
    result = _run_uscis(url, vintage_tag)
    print(json.dumps(result, indent=2))


@app.command(name="bls")
def bls_cmd(
    start: int = typer.Option(2010, "--start"),
    end: int = typer.Option(2024, "--end"),
) -> None:
    """Fetch BLS foreign-born series."""
    result = _run_bls(start, end)
    print(json.dumps(result, indent=2))


@app.command(name="pew")
def pew_cmd() -> None:
    """Parse a manually-downloaded Pew XLSX from data/raw/pew/."""
    result = _run_pew_local()
    print(json.dumps(result, indent=2))


@app.command(name="mpi")
def mpi_cmd() -> None:
    """Parse a manually-downloaded MPI XLSX from data/raw/mpi/."""
    result = _run_mpi_local()
    print(json.dumps(result, indent=2))


@app.command()
def all(
    years: list[int] = typer.Option(
        [2019, 2020, 2021, 2022, 2023], "--years", "-y"
    ),
) -> None:
    """Run every source. Failures in one source do not block the others."""
    settings = get_settings()
    settings.ensure_dirs()

    started = time.time()
    manifest = {
        "vintage": settings.census_acs_vintage,
        "results": {
            "census_acs": _run_census(years),
            "uscis_yearbook": _run_uscis(None, "2023"),
            "bls_lfs": _run_bls(2010, 2024),
            "pew": _run_pew_local(),
            "mpi": _run_mpi_local(),
        },
        "elapsed_sec": None,
    }
    manifest["elapsed_sec"] = round(time.time() - started, 1)

    manifest_path = settings.raw_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    log.info("Manifest written to %s", manifest_path)
    print(json.dumps(manifest, indent=2))


def main() -> None:
    """Entry point for `python -m migration_atlas.data.download`."""
    app()


if __name__ == "__main__":
    main()
