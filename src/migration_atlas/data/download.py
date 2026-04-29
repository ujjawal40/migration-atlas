"""Download raw data from public sources.

This is intentionally a stub for Phase 2 — it creates the directory layout and
documents which files should land where, so contributors know what to run.

In Phase 3 each function actually pulls and verifies the data. Census ACS is
fetched via the Census API; USCIS yearbook tables are scraped from the OHSS
site; MPI tabulations are downloaded as XLSX.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Data download CLI")


SOURCES = {
    "census_acs": {
        "description": "American Community Survey 1-year and 5-year tables",
        "url": "https://api.census.gov/data/2023/acs/acs1",
        "tables": ["B05002", "B05006", "B05007"],
        "license": "Public domain (U.S. government work)",
    },
    "uscis_yearbook": {
        "description": "OHSS Yearbook of Immigration Statistics",
        "url": "https://www.dhs.gov/ohss/topics/immigration/yearbook",
        "license": "Public domain",
    },
    "mpi_tabulations": {
        "description": "Migration Policy Institute Data Hub tabulations",
        "url": "https://www.migrationpolicy.org/programs/data-hub",
        "license": "Free for non-commercial use",
    },
    "bls_lfs": {
        "description": "BLS labor force statistics — foreign-born table A-7",
        "url": "https://www.bls.gov/cps/cpsaat07.htm",
        "license": "Public domain",
    },
    "oecd_dioc": {
        "description": "OECD Database on Immigrants in OECD Countries",
        "url": "https://www.oecd.org/els/mig/dioc.htm",
        "license": "OECD terms",
    },
}


@app.command()
def list_sources() -> None:
    """Print the source registry."""
    print(json.dumps(SOURCES, indent=2))


@app.command()
def all() -> None:
    """Download all sources. (Stub — populates raw/<source>/.gitkeep for now.)"""
    settings = get_settings()
    settings.ensure_dirs()
    for source in SOURCES:
        d = settings.raw_dir / source
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()
        log.info("Prepared %s", d)
    log.warning(
        "This is a stub. Real downloads will be implemented in Phase 3. "
        "For now, manually drop source files into data/raw/<source>/."
    )


def main() -> None:
    """Entry point for `python -m migration_atlas.data.download`."""
    app()


if __name__ == "__main__":
    main()
