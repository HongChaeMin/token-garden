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
    default=date.today().year,
    show_default=True,
    help="Year to display.",
)
def view(style: str, year: int):
    """Visualize token usage as a garden."""
    from token_garden.db import Database
    from token_garden.views.grid import GridView
    from token_garden.views.garden import GardenView

    console = Console()
    db = Database(_DEFAULT_DB)
    records = db.get_usage(year=year)
    db.close()

    if not records:
        console.print(
            f"[yellow]No data for {year}. Run [bold]token-garden sync[/bold] first.[/yellow]"
        )
        return

    if style == "grid":
        GridView(records, year=year).render(console)
    else:
        GardenView(records, year=year).render(console)
