import os
import tempfile
from datetime import date

import pytest

from token_garden.db import Database
from token_garden.providers.base import DailyUsage


@pytest.fixture
def db(tmp_path):
    return Database(tmp_path / "test.sqlite")


def test_upsert_and_query(db):
    usage = DailyUsage(date=date(2025, 3, 1), provider="claude",
                       input_tokens=1000, output_tokens=500)
    db.upsert([usage])

    rows = db.get_usage(year=2025)
    assert len(rows) == 1
    assert rows[0].date == date(2025, 3, 1)
    assert rows[0].total_tokens == 1500


def test_upsert_overwrites(db):
    u1 = DailyUsage(date=date(2025, 3, 1), provider="claude",
                    input_tokens=100, output_tokens=50)
    u2 = DailyUsage(date=date(2025, 3, 1), provider="claude",
                    input_tokens=200, output_tokens=100)
    db.upsert([u1])
    db.upsert([u2])

    rows = db.get_usage(year=2025)
    assert len(rows) == 1
    assert rows[0].total_tokens == 300


def test_get_usage_filters_by_year(db):
    u2024 = DailyUsage(date=date(2024, 12, 31), provider="claude",
                       input_tokens=100, output_tokens=50)
    u2025 = DailyUsage(date=date(2025, 1, 1), provider="claude",
                       input_tokens=200, output_tokens=100)
    db.upsert([u2024, u2025])

    rows = db.get_usage(year=2025)
    assert len(rows) == 1
    assert rows[0].date == date(2025, 1, 1)


def test_multiple_providers(db):
    claude = DailyUsage(date=date(2025, 3, 1), provider="claude",
                        input_tokens=1000, output_tokens=500)
    openai = DailyUsage(date=date(2025, 3, 1), provider="openai",
                        input_tokens=800, output_tokens=200)
    db.upsert([claude, openai])

    rows = db.get_usage(year=2025)
    assert len(rows) == 2
