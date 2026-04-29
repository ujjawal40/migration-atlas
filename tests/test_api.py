"""Smoke tests for the FastAPI backend."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from migration_atlas.api.main import app
    with TestClient(app) as c:
        yield c


class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestGraph:
    def test_returns_graph(self, client):
        r = client.get("/graph")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data and "links" in data
        assert len(data["nodes"]) > 30
        assert len(data["links"]) > 30


class TestQuery:
    def test_graph_lookup(self, client):
        r = client.post("/query", json={"query": "How is India connected to H-1B?"})
        assert r.status_code == 200
        data = r.json()
        assert data["handler"] == "graph_lookup"
        assert "india" in data["entities"]
        assert "h-1b" in data["entities"]
        assert data["sub_graph"] is not None
        assert len(data["sub_graph"]["nodes"]) > 0

    def test_forecast_unavailable(self, client):
        r = client.post("/query", json={"query": "Forecast Mexico in 5 years"})
        assert r.status_code == 200
        data = r.json()
        assert data["handler"] == "forecast"
        # Without trained model, we get a graceful fallback message
        assert data["answer"] is not None


class TestSentiment:
    def test_returns_zero_scores_without_checkpoint(self, client):
        """When the discourse-sentiment checkpoint is missing, the endpoint
        returns zero scores rather than 5xx, so the frontend can render an
        honest placeholder."""
        r = client.post("/sentiment", json={"text": "Some immigration speech."})
        assert r.status_code == 200
        data = r.json()
        assert data["model_loaded"] is False
        assert set(data["scores"]) == {
            "hostile", "welcoming", "dehumanizing", "assimilationist"
        }
        assert all(v == 0.0 for v in data["scores"].values())

    def test_text_echoed_in_response(self, client):
        r = client.post("/sentiment", json={"text": "Echo me."})
        assert r.status_code == 200
        assert r.json()["text"] == "Echo me."
