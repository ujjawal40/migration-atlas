"""Per-source ingest modules.

Each source has a `fetch(...)` that returns raw frames and a `process(...)` that
harmonizes those frames into the canonical schema documented in
`data/process.py`. The split exists so the network-bound and CPU-bound steps
can be cached and tested separately.
"""
from migration_atlas.data.sources import bls, census_acs, mpi, pew, uscis_yearbook, voteview

__all__ = ["census_acs", "uscis_yearbook", "bls", "pew", "mpi", "voteview"]
