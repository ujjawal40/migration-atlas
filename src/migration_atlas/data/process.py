"""Process raw data into harmonized parquet outputs.

Each source has a per-source processor. Outputs go to data/processed/ and feed
both the graph builder and the forecaster.
"""
from __future__ import annotations

import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Data processing CLI")


@app.command()
def all() -> None:
    """Process all available raw data sources."""
    settings = get_settings()
    settings.ensure_dirs()
    log.info("Processing pass — Phase 2 stub.")
    log.info(
        "Wiring per-source processors here in Phase 3. The shape we want:"
    )
    log.info("  - data/processed/foreign_born_by_country.parquet  (year, country, count)")
    log.info("  - data/processed/visa_issuance.parquet           (year, country, visa, count)")
    log.info("  - data/processed/flows.parquet                   (year, country, flow)")
    log.info("  - data/processed/labor_by_industry.parquet       (year, country, industry, count)")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
