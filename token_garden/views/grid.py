from __future__ import annotations

from datetime import date, timedelta

from rich.console import Console
from rich.text import Text

from token_garden.providers.base import DailyUsage

_ACTIVE_COLOR = "#26a641"
_EMPTY_COLOR = "#161b22"

_BLOCK = "█ "
_EMPTY = "░ "


class GridView:
    def __init__(self, records: list[DailyUsage], year: int):
        self._year = year
        self._daily: dict[date, int] = {}
        for r in records:
            self._daily[r.date] = self._daily.get(r.date, 0) + r.total_tokens

    def render(self, console: Console | None = None) -> None:
        if console is None:
            console = Console()

        console.print(f"\n[bold green]🌿 Token Garden — {self._year}[/bold green]\n")

        jan1 = date(self._year, 1, 1)
        dec31 = date(self._year, 12, 31)
        start = jan1 - timedelta(days=jan1.weekday())

        weeks: list[list[date | None]] = []
        current = start
        while current <= dec31 or len(weeks[-1]) < 7 if weeks else True:
            if not weeks or len(weeks[-1]) == 7:
                weeks.append([])
            d = current if current.year == self._year else None
            weeks[-1].append(d)
            current += timedelta(days=1)
            if current > dec31 and len(weeks[-1]) == 7:
                break

        # Month labels — 2 chars per week (letter + space) to match grid cell width
        month_labels = Text("     ")
        for week in weeks:
            first_real = next((d for d in week if d), None)
            if first_real and first_real.day <= 7:
                month_labels.append(first_real.strftime("%b")[0] + " ")
            else:
                month_labels.append("  ")
        console.print(month_labels)

        # Day rows (Mon=0 .. Sun=6)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for dow in range(7):
            row = Text(f"{day_names[dow]}  ")
            for week in weeks:
                d = week[dow] if dow < len(week) else None
                if d is None:
                    row.append("  ")
                else:
                    total = self._daily.get(d, 0)
                    if total > 0:
                        row.append(_BLOCK, style=_ACTIVE_COLOR)
                    else:
                        row.append(_EMPTY, style=_EMPTY_COLOR)
            console.print(row)

        total_year = sum(self._daily.values())
        peak_day = max(self._daily, key=self._daily.get) if self._daily else None

        legend = Text("\n")
        legend.append("░  없음  ", style=_EMPTY_COLOR)
        legend.append("█  사용", style=_ACTIVE_COLOR)
        console.print(legend)

        console.print(
            f"Total {self._year}: [green]{total_year:,}[/green] tokens"
            + (f"  |  Peak: [green]{peak_day}[/green] "
               f"({self._daily[peak_day]:,})" if peak_day else "")
        )
        console.print()
