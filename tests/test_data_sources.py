"""Tests for the data ingestion layer.

Network-dependent tests are skipped unless the relevant API key is available.
The harmonization helpers (country lookup, Yearbook label resolution, flow
merge) are tested directly with synthetic frames so the suite runs offline.
"""
from __future__ import annotations

import pandas as pd
import pytest

from migration_atlas.data import country_codes
from migration_atlas.data.process import process_flows


# ============================================================
# country_codes
# ============================================================
def test_canonical_id_lookup_exists_for_all_seed_countries():
    ids = country_codes.all_ids()
    assert len(ids) == 22
    assert "mexico" in ids
    assert "el-salvador" in ids


def test_iso3_round_trip():
    cc = country_codes.by_id("mexico")
    assert cc.iso3 == "MEX"
    assert country_codes.by_iso3("MEX").id == "mexico"


def test_label_resolution_handles_aliases():
    assert country_codes.by_label("People's Republic of China").id == "china"
    assert country_codes.by_label("Republic of Korea").id == "south-korea"
    assert country_codes.by_label("Great Britain").id == "uk"


def test_label_resolution_returns_none_for_unknown():
    assert country_codes.by_label("Atlantis") is None
    assert country_codes.by_label("") is None


def test_label_resolution_is_case_insensitive():
    assert country_codes.by_label("MEXICO").id == "mexico"
    assert country_codes.by_label("  Mexico  ").id == "mexico"


# ============================================================
# process_flows
# ============================================================
def test_process_flows_prefers_yearbook_over_acs_delta(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "processed"
    (raw / "uscis_yearbook").mkdir(parents=True)
    (raw / "census_acs").mkdir(parents=True)
    proc.mkdir()

    pd.DataFrame([
        {"country": "mexico", "year": 2020, "flow": 100_000},
        {"country": "mexico", "year": 2021, "flow": 110_000},
    ]).to_parquet(raw / "uscis_yearbook" / "visa_issuance.parquet", index=False)

    pd.DataFrame([
        {"country": "mexico", "year": 2019, "count": 11_000_000, "moe": 1000,
         "source": "census_acs_2019"},
        {"country": "mexico", "year": 2020, "count": 11_050_000, "moe": 1000,
         "source": "census_acs_2020"},
        {"country": "mexico", "year": 2021, "count": 11_100_000, "moe": 1000,
         "source": "census_acs_2021"},
    ]).to_parquet(raw / "census_acs" / "foreign_born.parquet", index=False)

    out = process_flows(raw, proc)
    assert out is not None
    df = pd.read_parquet(out)

    # 2020 and 2021 come from Yearbook
    yb = df[df["country"] == "mexico"].set_index("year")
    assert yb.loc[2020, "method"] == "uscis_yearbook"
    assert yb.loc[2020, "flow"] == 100_000
    assert yb.loc[2021, "method"] == "uscis_yearbook"


def test_process_flows_falls_back_to_acs_delta(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "processed"
    (raw / "census_acs").mkdir(parents=True)
    proc.mkdir()

    pd.DataFrame([
        {"country": "india", "year": 2019, "count": 3_000_000, "moe": 5000,
         "source": "census_acs_2019"},
        {"country": "india", "year": 2020, "count": 3_080_000, "moe": 5000,
         "source": "census_acs_2020"},
    ]).to_parquet(raw / "census_acs" / "foreign_born.parquet", index=False)

    out = process_flows(raw, proc)
    df = pd.read_parquet(out)
    row = df[(df["country"] == "india") & (df["year"] == 2020)].iloc[0]
    assert row["method"] == "acs_stock_delta"
    assert row["flow"] == 80_000


def test_process_flows_returns_none_when_no_sources(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "processed"
    raw.mkdir()
    proc.mkdir()
    assert process_flows(raw, proc) is None


# ============================================================
# Network-dependent — skipped without API keys
# ============================================================
@pytest.mark.integration
def test_census_variable_resolution_live():
    """Sanity check that the Census ACS variables endpoint still returns
    labels we can match against. Requires network; no API key needed for
    variables.json itself."""
    import httpx

    from migration_atlas.data.sources.census_acs import resolve_country_variables

    with httpx.Client() as client:
        var_map = resolve_country_variables(client, 2023, "acs1")
    # We expect to resolve at least the four largest origins.
    for cid in ("mexico", "india", "china", "philippines"):
        assert cid in var_map, f"Census 2023 ACS missing {cid} variable"
