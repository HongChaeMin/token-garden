from datetime import date

from token_garden.providers.base import DailyUsage
from token_garden.views.garden import GardenView, _plant_emoji, _week_number


def make_usage(d: date, total: int) -> DailyUsage:
    return DailyUsage(date=d, provider="claude",
                      input_tokens=total, output_tokens=0)


def test_plant_emoji_zero():
    assert _plant_emoji(0) == " "


def test_plant_emoji_levels():
    assert _plant_emoji(1) == "🌱"
    assert _plant_emoji(9_999) == "🌱"
    assert _plant_emoji(10_000) == "🌿"
    assert _plant_emoji(49_999) == "🌿"
    assert _plant_emoji(50_000) == "🌲"
    assert _plant_emoji(99_999) == "🌲"
    assert _plant_emoji(100_000) == "🌳"
    assert _plant_emoji(199_999) == "🌳"
    assert _plant_emoji(200_000) == "🌴"


def test_garden_view_renders_without_error():
    from rich.console import Console
    import io

    records = [
        make_usage(date(2025, 1, 1), 5_000),
        make_usage(date(2025, 1, 7), 80_000),
        make_usage(date(2025, 6, 15), 220_000),
    ]
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False)
    GardenView(records, year=2025).render(console)
    output = buf.getvalue()

    assert "2025" in output
    assert "🌴" in output
