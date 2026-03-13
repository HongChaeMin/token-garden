from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from token_garden.providers.base import DailyUsage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS token_usage (
    date          TEXT NOT NULL,
    provider      TEXT NOT NULL,
    input_tokens  INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, provider)
);
"""


class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def upsert(self, records: list[DailyUsage]) -> None:
        self._conn.executemany(
            """
            INSERT INTO token_usage (date, provider, input_tokens, output_tokens, total_tokens)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date, provider) DO UPDATE SET
                input_tokens  = excluded.input_tokens,
                output_tokens = excluded.output_tokens,
                total_tokens  = excluded.total_tokens
            """,
            [
                (r.date.isoformat(), r.provider, r.input_tokens,
                 r.output_tokens, r.total_tokens)
                for r in records
            ],
        )
        self._conn.commit()

    def get_usage(self, year: int) -> list[DailyUsage]:
        return self.get_usage_range(date(year, 1, 1), date(year, 12, 31))

    def get_usage_range(self, start: date, end: date) -> list[DailyUsage]:
        cursor = self._conn.execute(
            """
            SELECT date, provider, input_tokens, output_tokens, total_tokens
            FROM token_usage
            WHERE date BETWEEN ? AND ?
            ORDER BY date
            """,
            (start.isoformat(), end.isoformat()),
        )
        results = []
        for row in cursor.fetchall():
            usage = DailyUsage(
                date=date.fromisoformat(row[0]),
                provider=row[1],
                input_tokens=row[2],
                output_tokens=row[3],
            )
            usage.total_tokens = row[4]
            results.append(usage)
        return results

    def get_years(self) -> list[int]:
        cursor = self._conn.execute(
            "SELECT DISTINCT substr(date, 1, 4) FROM token_usage ORDER BY 1"
        )
        return [int(row[0]) for row in cursor.fetchall()]

    def close(self) -> None:
        self._conn.close()
