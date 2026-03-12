from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass
class DailyUsage:
    date: date
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int = field(init=False)

    def __post_init__(self):
        self.total_tokens = self.input_tokens + self.output_tokens


class Provider(ABC):
    @abstractmethod
    def fetch_usage(self, start_date: date, end_date: date) -> list[DailyUsage]:
        """Return daily usage records for the given date range."""
