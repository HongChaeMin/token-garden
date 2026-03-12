from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from token_garden.providers.base import DailyUsage, Provider

_DEFAULT_LOG_DIR = Path.home() / ".claude" / "projects"


class ClaudeProvider(Provider):
    def __init__(self, log_dir: Path | None = None):
        self._log_dir = Path(log_dir) if log_dir else _DEFAULT_LOG_DIR

    def fetch_usage(self, start_date: date, end_date: date) -> list[DailyUsage]:
        daily: dict[date, dict[str, int]] = defaultdict(
            lambda: {"input": 0, "output": 0}
        )

        for jsonl_file in self._log_dir.rglob("*.jsonl"):
            self._parse_file(jsonl_file, start_date, end_date, daily)

        return [
            DailyUsage(
                date=d,
                provider="claude",
                input_tokens=counts["input"],
                output_tokens=counts["output"],
            )
            for d, counts in sorted(daily.items())
            if start_date <= d <= end_date
        ]

    def _parse_file(
        self,
        path: Path,
        start_date: date,
        end_date: date,
        daily: dict,
    ) -> None:
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                self._parse_line(line.strip(), start_date, end_date, daily)
        except OSError:
            pass

    def _parse_line(
        self,
        line: str,
        start_date: date,
        end_date: date,
        daily: dict,
    ) -> None:
        if not line:
            return
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return

        if obj.get("type") != "assistant":
            return

        usage = obj.get("message", {}).get("usage")
        if not usage:
            return

        ts_str = obj.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            day = ts.astimezone(timezone.utc).date()
        except (ValueError, AttributeError):
            return

        if not (start_date <= day <= end_date):
            return

        daily[day]["input"] += usage.get("input_tokens", 0)
        daily[day]["output"] += usage.get("output_tokens", 0)

    # NOTE: Anthropic Usage API merge is not yet implemented.
    # Future task: add _merge_api_usage() once the Anthropic SDK exposes
    # a stable usage endpoint. Local log data is sufficient for now.
