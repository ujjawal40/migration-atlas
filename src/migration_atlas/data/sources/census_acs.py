"""Census American Community Survey (ACS) ingest.

Pulls foreign-born population by country of birth from table B05006 across
multiple ACS vintages. The variable codes (B05006_NNNE) shift between vintages
when the Census Bureau adds or reorganizes country detail, so this module
resolves them dynamically against the variables.json metadata endpoint rather
than hard-coding them.

Output schema:

    foreign_born_by_country.parquet
        country  (str, country id)
        year     (int)
        count    (int, foreign-born population)
        moe      (int, margin of error at 90%)
        source   (str, "census_acs_<vintage>")

Run as a CLI:

    python -m migration_atlas.data.sources.census_acs --years 2018 2019 2020 2021 2022 2023
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import httpx
import pandas as pd
import typer

from migration_atlas.data.country_codes import COUNTRIES
from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Census ACS ingest")

# B05006 = Place of Birth for the Foreign-Born Population in the United States.
TABLE = "B05006"


# ============================================================
# Variable resolution
# ============================================================
def _fetch_variable_metadata(client: httpx.Client, vintage: int, dataset: str) -> dict:
    """Pull the variables.json catalog for a given ACS vintage."""
    settings = get_settings()
    url = f"{settings.census_api_base}/{vintage}/acs/{dataset}/variables.json"
    log.info("Fetching ACS variable metadata: %s", url)
    r = client.get(url, timeout=30.0)
    r.raise_for_status()
    return r.json()["variables"]


def resolve_country_variables(
    client: httpx.Client, vintage: int, dataset: str
) -> dict[str, str]:
    """Map our canonical country ids → live ACS variable codes for B05006.

    Returns a dict like {"mexico": "B05006_150E", "india": "B05006_055E", ...}.
    Countries whose label does not match any live variable are omitted.
    """
    variables = _fetch_variable_metadata(client, vintage, dataset)
    out: dict[str, str] = {}

    # Filter to B05006 *_E (estimate) variables only; *_M are margins of error.
    for code, meta in variables.items():
        if not code.startswith(f"{TABLE}_"):
            continue
        if not code.endswith("E"):
            continue
        label = meta.get("label", "")
        # Labels look like "Estimate!!Total!!Asia!!Eastern Asia!!China"
        leaf = label.split("!!")[-1].strip()
        for c in COUNTRIES:
            if c.id in out:
                continue
            if leaf.lower() == c.census_label.lower():
                out[c.id] = code
                break

    missing = [c.id for c in COUNTRIES if c.id not in out]
    if missing:
        log.warning("Census %d: no B05006 variable matched %s", vintage, missing)
    log.info("Resolved %d/%d countries to ACS variables", len(out), len(COUNTRIES))
    return out


# ============================================================
# Data fetch
# ============================================================
def fetch_year(
    client: httpx.Client,
    vintage: int,
    dataset: str,
    api_key: str,
) -> pd.DataFrame:
    """Fetch one year of B05006 estimates for our seed countries."""
    settings = get_settings()
    var_map = resolve_country_variables(client, vintage, dataset)
    if not var_map:
        log.error("No ACS variables resolved for %d; skipping", vintage)
        return pd.DataFrame(columns=["country", "year", "count", "moe", "source"])

    # Census API caps `get` at 50 variables per request. We have ~22 estimates
    # plus ~22 margins of error, which fits comfortably.
    estimates = list(var_map.values())
    margins = [code[:-1] + "M" for code in estimates]  # B05006_150E -> B05006_150M
    get_clause = ",".join(["NAME"] + estimates + margins)

    url = f"{settings.census_api_base}/{vintage}/acs/{dataset}"
    params = {"get": get_clause, "for": "us:1", "key": api_key}
    log.info("Fetching ACS %d B05006 data", vintage)
    r = client.get(url, params=params, timeout=60.0)
    r.raise_for_status()
    rows = r.json()
    header, values = rows[0], rows[1]
    record = dict(zip(header, values, strict=True))

    out_rows = []
    for cid, est_code in var_map.items():
        moe_code = est_code[:-1] + "M"
        try:
            count = int(record[est_code])
            moe = int(record[moe_code])
        except (KeyError, ValueError, TypeError):
            log.warning("Bad value for %s in %d", cid, vintage)
            continue
        out_rows.append({
            "country": cid,
            "year": vintage,
            "count": count,
            "moe": moe,
            "source": f"census_acs_{vintage}",
        })
    return pd.DataFrame(out_rows)


def fetch_years(years: list[int]) -> pd.DataFrame:
    """Fetch B05006 across a range of ACS vintages and concatenate."""
    settings = get_settings()
    if not settings.census_api_key:
        raise RuntimeError(
            "CENSUS_API_KEY not set. Get one at https://api.census.gov/data/key_signup.html "
            "and add it to .env."
        )

    frames = []
    with httpx.Client(headers={"User-Agent": "migration-atlas/0.1"}) as client:
        for year in years:
            try:
                frame = fetch_year(
                    client, year, settings.census_acs_dataset, settings.census_api_key
                )
                frames.append(frame)
                # Census API has no published rate limit but we don't hammer it.
                time.sleep(0.5)
            except httpx.HTTPError as e:
                log.error("ACS %d failed: %s", year, e)

    if not frames:
        return pd.DataFrame(columns=["country", "year", "count", "moe", "source"])
    return pd.concat(frames, ignore_index=True)


# ============================================================
# Persist
# ============================================================
def write_raw(df: pd.DataFrame, raw_dir: Path) -> Path:
    """Write the harvested rows to data/raw/census_acs/foreign_born.parquet."""
    out_dir = raw_dir / "census_acs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "foreign_born.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d rows to %s", len(df), out_path)
    # Also drop a JSON sidecar with the variable resolution for auditability.
    sidecar = {"vintages": sorted(df["year"].unique().tolist()) if not df.empty else []}
    (out_dir / "manifest.json").write_text(json.dumps(sidecar, indent=2))
    return out_path


# ============================================================
# CLI
# ============================================================
@app.command()
def fetch(
    years: list[int] = typer.Option(
        [2019, 2020, 2021, 2022, 2023], "--years", "-y", help="ACS vintages"
    ),
) -> None:
    """Fetch ACS B05006 across the given vintages and write to raw/."""
    settings = get_settings()
    settings.ensure_dirs()
    df = fetch_years(years)
    if df.empty:
        log.warning("No rows fetched; nothing written.")
        return
    write_raw(df, settings.raw_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
