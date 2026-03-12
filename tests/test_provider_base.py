from datetime import date
from token_garden.providers.base import DailyUsage, Provider


def test_daily_usage_total():
    usage = DailyUsage(
        date=date(2025, 3, 1),
        provider="claude",
        input_tokens=1000,
        output_tokens=500,
    )
    assert usage.total_tokens == 1500


def test_provider_is_abstract():
    import pytest
    with pytest.raises(TypeError):
        Provider()  # cannot instantiate ABC
