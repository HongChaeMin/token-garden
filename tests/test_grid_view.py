from datetime import date

from token_garden.providers.base import DailyUsage
from token_garden.views.grid import GridView, _intensity, _compute_thresholds


def make_usage(d: date, total: int) -> DailyUsage:
    return DailyUsage(date=d, provider="claude",
                      input_tokens=total, output_tokens=0)


def test_intensity_zero():
    thresholds = _compute_thresholds([1, 10_000, 50_000, 100_000, 200_000])
    assert _intensity(0, thresholds) == 0


def test_intensity_levels():
    thresholds = [1, 10_000, 50_000, 100_000, 200_000]
    assert _intensity(1, thresholds) == 1
    assert _intensity(10_000, thresholds) == 2
    assert _intensity(50_000, thresholds) == 3
    assert _intensity(100_000, thresholds) == 4
    assert _intensity(200_000, thresholds) == 5
    assert _intensity(999_999, thresholds) == 5


def test_grid_view_renders_without_error():
    from rich.console import Console
    import io

    records = [
        make_usage(date(2025, 1, 1), 5_000),
        make_usage(date(2025, 6, 15), 80_000),
        make_usage(date(2025, 12, 31), 150_000),
    ]
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False)
    GridView(records, date(2025, 1, 1), date(2025, 12, 31)).render(console)
    output = buf.getvalue()

    assert "2025" in output
    assert len(output) > 0
