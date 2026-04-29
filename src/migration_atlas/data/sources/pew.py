"""Pew Research Center — unauthorized population estimates.

Pew publishes the residual-method unauthorized estimates as XLSX files attached
to its periodic reports (most recently the 2024 update with 2022 estimates).
There is no API. The user drops the XLSX into

    data/raw/pew/unauthorized_estimates.xlsx

and this module parses it. We document the upstream URL but do not auto-fetch
because Pew's URL paths change between reports and the file is small enough
that manual placement is not a real friction.

Output schema:

    pew_unauthorized.parquet
        country     (str, country id)
        year        (int)
        unauth_pop  (int, estimated unauthorized residents)
        source      (str, "pew_<report_year>")
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from migration_atlas.data.country_codes import by_label
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Pew ingest")


def parse(xlsx_path: Path) -> pd.DataFrame:
    """Parse the Pew unauthorized-estimates XLSX into a long frame."""
    sheets = pd.read_excel(xlsx_path, sheet_name=None, header=None)
    rows: list[dict] = []
    for name, frame in sheets.items():
        flat = frame.astype(str).head(5).agg(" ".join, axis=1).str.lower()
        if not flat.str.contains("unauthorized").any():
            continue
        log.info("Parsing Pew sheet %r", name)
        # Heuristic: first object column is the country, integer columns are years.
        df = pd.read_excel(xlsx_path, sheet_name=name, header=2)
        df = df.dropna(how="all")
        country_col = next((c for c in df.columns if df[c].dtype == object), None)
        if country_col is None:
            continue
        year_cols = [c for c in df.columns if isinstance(c, int) and 1990 < c < 2100]
        for _, r in df.iterrows():
            cc = by_label(str(r[country_col]))
            if cc is None:
                continue
            for y in year_cols:
                val = pd.to_numeric(r[y], errors="coerce")
                if pd.isna(val):
                    continue
                rows.append({
                    "country": cc.id,
                    "year": int(y),
                    "unauth_pop": int(val),
                })
    return pd.DataFrame(rows)


def write_raw(df: pd.DataFrame, raw_dir: Path, report_year: int) -> Path:
    out_dir = raw_dir / "pew"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source=f"pew_{report_year}")
    out_path = out_dir / "unauthorized.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    return out_path


@app.command()
def fetch(
    xlsx: Path = typer.Option(..., "--xlsx", help="Path to the Pew XLSX"),
    report_year: int = typer.Option(2024, "--report-year"),
) -> None:
    """Parse a manually-downloaded Pew XLSX into raw/."""
    settings = get_settings()
    settings.ensure_dirs()
    if not xlsx.exists():
        raise typer.BadParameter(f"{xlsx} not found")
    df = parse(xlsx)
    if df.empty:
        log.warning("No rows parsed; check the sheet structure.")
        return
    write_raw(df, settings.raw_dir, report_year)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
