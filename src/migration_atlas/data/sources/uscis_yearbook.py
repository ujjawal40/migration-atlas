"""USCIS / Office of Homeland Security Statistics — Yearbook of Immigration Statistics.

Pulls Table 3 (Persons Obtaining Lawful Permanent Resident Status by Region and
Country of Birth) from the published Yearbook XLSX. This is the authoritative
source for legal-flow series back to 1820, though the earlier records are
sparse and the modern run with full country detail begins in 1986.

The Yearbook ships as a multi-sheet Excel file. We pull two sheets per release:

    Table 3 — annual flow (LPR adjustments + new arrivals) by country
    Table 6 — H-1B / F-1 / EB-* approvals by country, when available

The XLSX URL changes annually as new vintages are published. We fetch the URL
configured in `Settings.uscis_yearbook_url`, falling back to a manually-placed
file in `data/raw/uscis_yearbook/`.

Output schema:

    visa_issuance.parquet
        country  (str, country id)
        year     (int)
        flow     (int, LPR-status acquisitions in that fiscal year)
        source   (str, "uscis_yearbook_<vintage>")
"""
from __future__ import annotations

from pathlib import Path

import httpx
import pandas as pd
import typer

from migration_atlas.data.country_codes import by_label
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="USCIS Yearbook ingest")


# ============================================================
# Fetch
# ============================================================
def download(url: str, dest: Path, force: bool = False) -> Path:
    """Download the Yearbook XLSX if not already present."""
    if dest.exists() and not force:
        log.info("Using cached Yearbook at %s", dest)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    log.info("Downloading USCIS Yearbook: %s", url)
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


# ============================================================
# Parse
# ============================================================
def _find_country_column(df: pd.DataFrame) -> str:
    """Yearbook tables put the country name in the first column, but the column
    label varies ("Country of Birth", "Region/country of birth", etc.).
    Pick the first object-typed column."""
    for col in df.columns:
        if df[col].dtype == object:
            return col
    raise ValueError("No string column found in Yearbook frame")


def parse_table3(xlsx_path: Path) -> pd.DataFrame:
    """Parse the Table 3 sheet (LPR by country) into a long DataFrame.

    Recent Yearbooks use a sheet named like 'Table 3' or 'Table 3D'. The
    structure is wide: one country per row, fiscal years as columns.
    """
    sheets = pd.read_excel(xlsx_path, sheet_name=None, header=None)
    # Find the sheet whose first non-null cell mentions "Persons Obtaining" — robust
    # to year-to-year reformatting.
    target = None
    for name, frame in sheets.items():
        flat = frame.astype(str).head(5).agg(" ".join, axis=1).str.lower()
        if flat.str.contains("persons obtaining").any():
            target = (name, frame)
            break
    if target is None:
        raise ValueError(f"Could not locate Table 3 sheet in {xlsx_path}")

    name, frame = target
    log.info("Using sheet %r as Table 3", name)

    # Find the header row (first row that contains "Total" and at least one 4-digit year).
    header_row = None
    for i in range(min(20, len(frame))):
        row = frame.iloc[i].astype(str)
        years = [c for c in row if c.strip().isdigit() and 1900 < int(c) < 2100]
        if "Total" in row.values and len(years) >= 3:
            header_row = i
            break
    if header_row is None:
        raise ValueError("Could not locate header row in Table 3")

    df = pd.read_excel(xlsx_path, sheet_name=name, header=header_row)
    df = df.dropna(how="all")
    country_col = _find_country_column(df)

    # Years are integer-typed columns
    year_cols = [c for c in df.columns if isinstance(c, int) and 1900 < c < 2100]
    if not year_cols:
        raise ValueError("No year columns found after header parse")

    long = df[[country_col, *year_cols]].melt(
        id_vars=[country_col], var_name="year", value_name="flow"
    )
    long = long.rename(columns={country_col: "label"})
    long["flow"] = pd.to_numeric(long["flow"], errors="coerce")
    long = long.dropna(subset=["flow", "label"])
    long["year"] = long["year"].astype(int)
    long["flow"] = long["flow"].astype(int)
    return long


def harmonize(long: pd.DataFrame) -> pd.DataFrame:
    """Map free-text country labels to canonical country ids; drop unknowns."""
    rows = []
    unknown: set[str] = set()
    for _, r in long.iterrows():
        cc = by_label(str(r["label"]))
        if cc is None:
            unknown.add(str(r["label"]))
            continue
        rows.append({"country": cc.id, "year": int(r["year"]), "flow": int(r["flow"])})
    if unknown:
        log.info(
            "Yearbook: %d labels not in seed (e.g. %s)",
            len(unknown), sorted(unknown)[:5],
        )
    return pd.DataFrame(rows)


# ============================================================
# Persist
# ============================================================
def write_raw(df: pd.DataFrame, raw_dir: Path, vintage_tag: str) -> Path:
    out_dir = raw_dir / "uscis_yearbook"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source=f"uscis_yearbook_{vintage_tag}")
    out_path = out_dir / "visa_issuance.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    return out_path


# ============================================================
# CLI
# ============================================================
@app.command()
def fetch(
    url: str = typer.Option(None, "--url", help="Override the Yearbook XLSX URL"),
    local: Path = typer.Option(None, "--local", help="Use a local XLSX (skip download)"),
    vintage_tag: str = typer.Option("2023", "--vintage"),
) -> None:
    """Fetch and parse the USCIS Yearbook into raw/."""
    settings = get_settings()
    settings.ensure_dirs()
    if local is not None:
        xlsx_path = local
    else:
        url = url or settings.uscis_yearbook_url
        xlsx_path = download(
            url, settings.raw_dir / "uscis_yearbook" / f"yearbook_{vintage_tag}.xlsx"
        )
    long = parse_table3(xlsx_path)
    canonical = harmonize(long)
    write_raw(canonical, settings.raw_dir, vintage_tag)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
