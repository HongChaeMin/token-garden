from __future__ import annotations

from datetime import date
from pathlib import Path

import click
from rich.console import Console

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
    _sync(db, console)  # log_dir=None → uses default ~/.claude/projects
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
    help="Year to display (default: current year).",
)
@click.option(
    "--all", "show_all",
    is_flag=True,
    default=False,
    help="Show all years with data.",
)
def view(style: str, year: int | None, show_all: bool):
    """Visualize token usage as a garden."""
    from token_garden.db import Database
    from token_garden.views.grid import GridView
    from token_garden.views.garden import GardenView

    console = Console()
    db = Database(_DEFAULT_DB)

    if show_all:
        years = db.get_years()
        if not years:
            console.print("[yellow]No data. Run [bold]token-garden sync[/bold] first.[/yellow]")
            db.close()
            return
    else:
        years = [year or date.today().year]

    for y in years:
        records = db.get_usage(year=y)
        if not records:
            console.print(
                f"[yellow]No data for {y}. Run [bold]token-garden sync[/bold] first.[/yellow]"
            )
            continue
        if style == "grid":
            GridView(records, year=y).render(console)
        else:
            GardenView(records, year=y).render(console)

    db.close()
