import json
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from token_garden.cli import cli
from token_garden.db import Database
from token_garden.providers.base import DailyUsage


@pytest.fixture
def runner():
    return CliRunner()


def test_view_no_data_shows_hint(runner, tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setattr("token_garden.cli._DEFAULT_DB", db_path)
    monkeypatch.setattr("token_garden.sync.sync", lambda db, console, **kw: None)

    result = runner.invoke(cli, ["view"])
    assert result.exit_code == 0
    assert "sync" in result.output


def test_view_grid_with_data(runner, tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setattr("token_garden.cli._DEFAULT_DB", db_path)

    db = Database(db_path)
    db.upsert([DailyUsage(date=date(2025, 6, 1), provider="claude",
                           input_tokens=50_000, output_tokens=10_000)])
    db.close()

    result = runner.invoke(cli, ["view", "--year", "2025"])
    assert result.exit_code == 0
    assert "2025" in result.output


def test_view_garden_with_data(runner, tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setattr("token_garden.cli._DEFAULT_DB", db_path)

    db = Database(db_path)
    db.upsert([DailyUsage(date=date(2025, 6, 1), provider="claude",
                           input_tokens=50_000, output_tokens=10_000)])
    db.close()

    result = runner.invoke(cli, ["view", "--style", "garden", "--year", "2025"])
    assert result.exit_code == 0
    assert "2025" in result.output
