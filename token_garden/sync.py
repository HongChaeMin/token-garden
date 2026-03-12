from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.console import Console

from token_garden.db import Database
from token_garden.providers.claude import ClaudeProvider

# Collect from epoch so all local log history is captured
_EPOCH = date(2020, 1, 1)


def sync(
    db: Database,
    console: Console,
    log_dir: Path | None = None,
) -> None:
    """Collect token data from all configured providers and store in db.

    Local logs: collected all-time (from 2020-01-01 to today).
    """
    end = date.today()
    provider = ClaudeProvider(log_dir=log_dir)

    console.print("🔍 [dim]Collecting from Claude Code logs...[/dim]", end=" ")
    records = provider.fetch_usage(_EPOCH, end)
    console.print(f"[green]✓ {len(records)} days[/green]")

    db.upsert(records)
    console.print(f"💾 [dim]Saved to[/dim] [green]{db.path}[/green] [green]✓[/green]")
