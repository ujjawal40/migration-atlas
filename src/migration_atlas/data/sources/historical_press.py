"""Chronicling America — historical newspaper text (Library of Congress).

The Library of Congress runs a public OCR'd corpus of U.S. newspapers from
1777 to 1963. We use the JSON search API to pull articles that mention the
nationality slurs and immigration-policy phrases relevant to the discourse
corpus, by date range.

API docs: https://chroniclingamerica.loc.gov/about/api/
No key required. Rate limit: be polite.

Output schema:

    historical_press.parquet
        article_id   (str, LCCN+date+seq)
        title        (str)
        date         (str, YYYY-MM-DD)
        newspaper    (str)
        state        (str, USPS code)
        excerpt      (str, first ~600 chars of OCR text)
        url          (str, deep link)
        query        (str, the search query that surfaced it)
        source       ('chronicling_america')
"""
from __future__ import annotations

import time
from pathlib import Path

import httpx
import pandas as pd
import typer

from migration_atlas.utils import get_logger, get_settings

log = get_logger(__name__)
app = typer.Typer(help="Chronicling America ingest")

API_BASE = "https://chroniclingamerica.loc.gov/search/pages/results/"

# Default queries cover the major immigration-discourse moments we want
# coverage for. The corpus is 1777-1963 so post-1965 events are out of scope.
DEFAULT_QUERIES = [
    ("chinese exclusion", 1880, 1905),
    ("johnson-reed", 1921, 1928),
    ("national origins quota", 1923, 1965),
    ("bracero", 1942, 1965),
    ("displaced persons", 1945, 1955),
    ("hungarian refugee", 1956, 1962),
    ("undesirable alien", 1900, 1924),
]


def search(
    client: httpx.Client,
    phrase: str,
    start_year: int,
    end_year: int,
    max_results: int = 200,
) -> list[dict]:
    """Run one Chronicling America phrase search and return up to max_results."""
    rows: list[dict] = []
    page = 1
    while len(rows) < max_results:
        params = {
            "andtext": phrase,
            "dateFilterType": "yearRange",
            "date1": str(start_year),
            "date2": str(end_year),
            "rows": "50",
            "page": str(page),
            "format": "json",
        }
        log.info("CA search '%s' page %d", phrase, page)
        r = client.get(API_BASE, params=params, timeout=60.0)
        r.raise_for_status()
        body = r.json()
        items = body.get("items", [])
        if not items:
            break
        for it in items:
            rows.append({
                "article_id": it.get("id"),
                "title": (it.get("title") or "").strip(),
                "date": _normalize_date(it.get("date")),
                "newspaper": it.get("title_normal") or it.get("title"),
                "state": (it.get("state") or [None])[0],
                "excerpt": (it.get("ocr_eng") or "")[:600],
                "url": "https://chroniclingamerica.loc.gov" + (it.get("id") or ""),
                "query": phrase,
            })
        if len(items) < 50:
            break
        page += 1
        time.sleep(0.5)
    return rows[:max_results]


def _normalize_date(raw: str | None) -> str | None:
    if not raw or len(raw) < 8:
        return None
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def fetch_default_queries(max_per_query: int = 200) -> pd.DataFrame:
    """Run all default queries and return one combined DataFrame."""
    all_rows: list[dict] = []
    with httpx.Client(headers={"User-Agent": "migration-atlas/0.1"}) as client:
        for phrase, start, end in DEFAULT_QUERIES:
            try:
                all_rows.extend(search(client, phrase, start, end, max_per_query))
            except httpx.HTTPError as e:
                log.error("CA search failed for '%s': %s", phrase, e)
    return pd.DataFrame(all_rows)


def write_raw(df: pd.DataFrame, raw_dir: Path) -> Path:
    out_dir = raw_dir / "chronicling_america"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = df.assign(source="chronicling_america")
    out_path = out_dir / "articles.parquet"
    df.to_parquet(out_path, index=False)
    log.info("Wrote %d articles to %s", len(df), out_path)
    return out_path


@app.command()
def fetch(
    max_per_query: int = typer.Option(200, "--max-per-query"),
) -> None:
    """Run all default queries and persist the union."""
    settings = get_settings()
    settings.ensure_dirs()
    df = fetch_default_queries(max_per_query)
    if df.empty:
        log.warning("No articles fetched.")
        return
    write_raw(df, settings.raw_dir)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
