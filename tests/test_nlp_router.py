"""Tests for the NLP query router."""
from __future__ import annotations

import pytest

from migration_atlas.nlp.router import parse_query


class TestEntityExtraction:
    @pytest.mark.parametrize("q,expected", [
        ("How is India connected to H-1B?", {"india", "h-1b"}),
        ("Tell me about Mexico", {"mexico"}),
        ("Compare China and Vietnam", {"china", "vietnam"}),
        ("What did the 1965 act do?", {"ina-1965"}),
        ("Hart-Celler effects", {"ina-1965"}),
        ("How did the Chinese Exclusion Act affect migration?",
         {"chinese-exclusion-1882", "china"}),
    ])
    def test_finds_entities(self, q, expected):
        plan = parse_query(q)
        assert expected.issubset(set(plan.entities))


class TestIntentDetection:
    @pytest.mark.parametrize("q,handler", [
        ("Forecast Mexico migration", "forecast"),
        ("predict India flow next 5 years", "forecast"),
        ("Find countries similar to Vietnam", "similarity"),
        ("What is the wage effect of low-skill immigration?", "rag"),
        ("How is India connected to H-1B?", "graph_lookup"),
    ])
    def test_classifies(self, q, handler):
        plan = parse_query(q)
        assert plan.handler == handler


class TestHorizonExtraction:
    def test_in_5_years(self):
        plan = parse_query("Forecast India flows in 5 years")
        assert plan.horizon == 5

    def test_next_3_years(self):
        plan = parse_query("Predict Mexico migration next 3 years")
        assert plan.horizon == 3

    def test_no_horizon(self):
        plan = parse_query("How is India connected to H-1B?")
        assert plan.horizon is None
