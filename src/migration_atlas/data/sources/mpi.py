"""Migration Policy Institute — pre-aggregated tabulations.

MPI publishes country-of-origin tabulations through its Data Hub
(migrationpolicy.org/programs/data-hub). The downloads are XLSX/CSV with stable
column conventions, but no public API. The user drops the file at

    data/raw/mpi/country_profiles.xlsx

and this module parses it. MPI is the easiest way to obtain historical series
back to 1850 for the largest origins.

Output schema:

    mpi_profiles.parquet
        country      (str, country id)
        year         (int)
        metric       (str, e.g. "foreign_born_us", "median_household_income")
        value        (float)
        source       (str, "mpi_data_hub")
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.data.country_codes import by_label
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="MPI ingest")


def parse(xlsx_path: Path) -> pd.DataFrame:
    """Parse an MPI Data Hub export into a long frame."""
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    rows: list[dict] = []
    for sheet_name, df in sheets.items():
        if df.empty:
            continue
        country_col = next((c for c in df.columns if df[c].dtype == object), None)
        if country_col is None:
            continue
        for _, r in df.iterrows():
            cc = by_label(str(r[country_col]))
            if cc is None:
                continue
            for col, val in r.items():
                if col == country_col:
                    continue
                num = pd.to_numeric(val, errors="coerce")
                if pd.isna(num):
                    continue
                # If the column header is a year, store as a yearly metric.
                if isinstance(col, int) and 1800 < col < 2100:
                    rows.append({
                        "country": cc.id,
                        "year": col,
                        "metric": sheet_name.lower().replace(" ", "_"),
                        "value": float(num),
                    })
                else:
                    rows.append({
                        "country": cc.id,
                        "year": pd.NA,
                        "metric": str(col).lower().replace(" ", "_"),
                        "value": float(num),
                    })
    return pd.DataFrame(rows)


def write_raw(df: pd.DataFrame, raw_dir: Path) -> Path:
    out_dir = raw_dir / "mpi"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source="mpi_data_hub")
    out_path = out_dir / "profiles.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    return out_path


@app.command()
def fetch(
    xlsx: Path = typer.Option(..., "--xlsx", help="Path to the MPI XLSX export"),
) -> None:
    """Parse a manually-downloaded MPI Data Hub export."""
    settings = get_settings()
    settings.ensure_dirs()
    if not xlsx.exists():
        raise typer.BadParameter(f"{xlsx} not found")
    df = parse(xlsx)
    if df.empty:
        log.warning("No rows parsed.")
        return
    write_raw(df, settings.raw_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
