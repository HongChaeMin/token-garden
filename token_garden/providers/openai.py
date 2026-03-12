from __future__ import annotations

from datetime import date

from token_garden.providers.base import DailyUsage, Provider


class OpenAIProvider(Provider):
    """Stub — not yet implemented. Raises NotImplementedError."""

    def fetch_usage(self, start_date: date, end_date: date) -> list[DailyUsage]:
        raise NotImplementedError(
            "OpenAI provider is not yet implemented. "
            "Contributions welcome — implement fetch_usage() using "
            "the OpenAI usage API."
        )
