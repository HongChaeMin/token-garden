from datetime import date

from token_garden.providers.base import DailyUsage
from token_garden.views.grid import GridView


def make_usage(d: date, total: int) -> DailyUsage:
    return DailyUsage(date=d, provider="claude",
                      input_tokens=total, output_tokens=0)


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
    GridView(records, year=2025).render(console)
    output = buf.getvalue()

    assert "2025" in output
    assert len(output) > 0


def test_grid_view_empty_days_show_empty_char():
    import io
    from rich.console import Console

    records = []
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False)
    GridView(records, year=2025).render(console)
    output = buf.getvalue()

    assert "░" in output


def test_grid_view_active_days_show_block_char():
    import io
    from rich.console import Console

    records = [make_usage(date(2025, 6, 15), 10_000)]
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False)
    GridView(records, year=2025).render(console)
    output = buf.getvalue()

    assert "█" in output
