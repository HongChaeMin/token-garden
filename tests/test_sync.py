import json
from datetime import date
from pathlib import Path

import pytest
from rich.console import Console

from token_garden.db import Database
from token_garden.sync import sync


@pytest.fixture
def log_dir(tmp_path):
    proj = tmp_path / "proj1"
    proj.mkdir()
    conv = proj / "conv1.jsonl"
    conv.write_text(
        json.dumps({
            "type": "assistant",
            "timestamp": "2024-06-15T10:00:00Z",
            "message": {"usage": {"input_tokens": 500, "output_tokens": 200}},
        }) + "\n" +
        json.dumps({
            "type": "assistant",
            "timestamp": "2025-03-01T10:00:00Z",
            "message": {"usage": {"input_tokens": 1000, "output_tokens": 400}},
        })
    )
    return tmp_path


def test_sync_writes_to_db(log_dir, tmp_path):
    db = Database(tmp_path / "test.sqlite")
    console = Console(quiet=True)

    sync(db, console, log_dir=log_dir)

    # Both years should be collected from local logs
    rows_2024 = db.get_usage(year=2024)
    rows_2025 = db.get_usage(year=2025)
    assert len(rows_2024) == 1
    assert rows_2024[0].total_tokens == 700
    assert len(rows_2025) == 1
    assert rows_2025[0].total_tokens == 1400
    db.close()
