from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import click
from rich.console import Console

import token_garden.sync as _sync_module

_DEFAULT_DB = Path.home() / ".token-garden" / "db.sqlite"


@click.group()
def cli():
    """🌿 Token Garden — visualize your LLM token usage."""


@cli.command()
def sync():
    """Collect and cache token usage data."""
    from token_garden.db import Database
    from token_garden.sync import sync as _sync

    console = Console()
    db = Database(_DEFAULT_DB)
    _sync(db, console)
    db.close()


@cli.command()
@click.option(
    "--style",
    type=click.Choice(["grid", "garden"]),
    default="grid",
    show_default=True,
    help="Visualization style.",
)
@click.option(
    "--year",
    type=int,
    default=None,
    help="Calendar year to display.",
)
@click.option(
    "--all", "show_all",
    is_flag=True,
    default=False,
    help="Show all years with data.",
)
def view(style: str, year: int | None, show_all: bool):
    """Visualize token usage as a garden (default: last 365 days)."""
    from token_garden.db import Database
    from token_garden.views.grid import GridView
    from token_garden.views.garden import GardenView

    console = Console()
    db = Database(_DEFAULT_DB)
    _sync_module.sync(db, console)

    if show_all:
        years = db.get_years()
        if not years:
            console.print("[yellow]No data found.[/yellow]")
            db.close()
            return
        for y in years:
            records = db.get_usage(year=y)
            if not records:
                continue
            if style == "grid":
                GridView(records, date(y, 1, 1), date(y, 12, 31)).render(console)
            else:
                GardenView(records, year=y).render(console)
    elif year:
        records = db.get_usage(year=year)
        if not records:
            console.print(f"[yellow]No data for {year}.[/yellow]")
        elif style == "grid":
            GridView(records, date(year, 1, 1), date(year, 12, 31)).render(console)
        else:
            GardenView(records, year=year).render(console)
    else:
        # default: last 365 days
        end = date.today()
        start = end - timedelta(days=364)
        records = db.get_usage_range(start, end)
        if not records:
            console.print("[yellow]No data. Run [bold]token-garden sync[/bold] first.[/yellow]")
        elif style == "grid":
            GridView(records, start, end).render(console)
        else:
            # garden view는 연도 단위라 올해로 fallback
            GardenView(db.get_usage(year=end.year), year=end.year).render(console)

    db.close()
