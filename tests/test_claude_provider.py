import json
from datetime import date
from pathlib import Path

import pytest

from token_garden.providers.claude import ClaudeProvider


@pytest.fixture
def log_dir(tmp_path):
    """Create fake Claude Code log structure."""
    project_dir = tmp_path / "proj1"
    project_dir.mkdir()
    return tmp_path


def write_jsonl(path: Path, lines: list[dict]):
    path.write_text("\n".join(json.dumps(l) for l in lines))


def test_parses_assistant_messages(log_dir):
    write_jsonl(log_dir / "proj1" / "conv1.jsonl", [
        {
            "type": "assistant",
            "timestamp": "2025-03-01T10:00:00Z",
            "message": {"usage": {"input_tokens": 1000, "output_tokens": 500}},
        },
        {
            "type": "user",
            "timestamp": "2025-03-01T10:01:00Z",
            "message": {"content": "hello"},
        },
    ])

    provider = ClaudeProvider(log_dir=log_dir)
    result = provider.fetch_usage(date(2025, 3, 1), date(2025, 3, 1))

    assert len(result) == 1
    assert result[0].date == date(2025, 3, 1)
    assert result[0].input_tokens == 1000
    assert result[0].output_tokens == 500
    assert result[0].provider == "claude"


def test_aggregates_multiple_messages_same_day(log_dir):
    write_jsonl(log_dir / "proj1" / "conv2.jsonl", [
        {
            "type": "assistant",
            "timestamp": "2025-03-01T09:00:00Z",
            "message": {"usage": {"input_tokens": 500, "output_tokens": 200}},
        },
        {
            "type": "assistant",
            "timestamp": "2025-03-01T11:00:00Z",
            "message": {"usage": {"input_tokens": 300, "output_tokens": 100}},
        },
    ])

    provider = ClaudeProvider(log_dir=log_dir)
    result = provider.fetch_usage(date(2025, 3, 1), date(2025, 3, 1))

    assert len(result) == 1
    assert result[0].input_tokens == 800
    assert result[0].output_tokens == 300


def test_filters_by_date_range(log_dir):
    write_jsonl(log_dir / "proj1" / "conv3.jsonl", [
        {
            "type": "assistant",
            "timestamp": "2025-02-28T23:59:00Z",
            "message": {"usage": {"input_tokens": 999, "output_tokens": 1}},
        },
        {
            "type": "assistant",
            "timestamp": "2025-03-01T00:00:00Z",
            "message": {"usage": {"input_tokens": 100, "output_tokens": 50}},
        },
    ])

    provider = ClaudeProvider(log_dir=log_dir)
    result = provider.fetch_usage(date(2025, 3, 1), date(2025, 3, 31))

    assert len(result) == 1
    assert result[0].date == date(2025, 3, 1)


def test_skips_malformed_lines(log_dir):
    path = log_dir / "proj1" / "conv4.jsonl"
    path.write_text('{"type": "assistant", "timestamp": "2025-03-01T10:00:00Z"}\n'
                    'not-json\n'
                    '{"type": "assistant", "timestamp": "2025-03-01T11:00:00Z", '
                    '"message": {"usage": {"input_tokens": 100, "output_tokens": 50}}}\n')

    provider = ClaudeProvider(log_dir=log_dir)
    result = provider.fetch_usage(date(2025, 3, 1), date(2025, 3, 1))

    assert len(result) == 1
    assert result[0].input_tokens == 100
