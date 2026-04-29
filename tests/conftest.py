"""Shared pytest fixtures."""
from __future__ import annotations

import pytest

from migration_atlas.graph.build import build_default
from migration_atlas.graph.schema import GraphSpec


@pytest.fixture(scope="session")
def graph_backend():
    """Cached default NetworkX graph."""
    return build_default()


@pytest.fixture(scope="session")
def graph_spec() -> GraphSpec:
    from migration_atlas.graph.build import to_spec
    return to_spec()
