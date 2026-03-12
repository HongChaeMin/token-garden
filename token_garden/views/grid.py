from __future__ import annotations

from datetime import date, timedelta

from rich.console import Console
from rich.text import Text

from token_garden.providers.base import DailyUsage

# (total_tokens) → intensity level 0-4
_THRESHOLDS = [0, 1, 10_000, 50_000, 100_000]

_COLORS = [
    "#161b22",  # 0: empty
    "#0e4429",  # 1: dark green
    "#006d32",  # 2: medium green
    "#26a641",  # 3: green
    "#39d353",  # 4: bright green
]

_BLOCK = "█"
_EMPTY = "░"


def _intensity(total: int) -> int:
    if total <= 0:
        return 0
    for level in range(4, 0, -1):
        if total >= _THRESHOLDS[level]:
            return level
    return 1


class GridView:
    def __init__(self, records: list[DailyUsage], year: int):
        self._year = year
        # Aggregate across providers: sum by date
        self._daily: dict[date, int] = {}
        for r in records:
            self._daily[r.date] = self._daily.get(r.date, 0) + r.total_tokens

    def render(self, console: Console | None = None) -> None:
        if console is None:
            console = Console()

        console.print(f"\n[bold green]🌿 Token Garden — {self._year}[/bold green]\n")

        # Build week columns: each column = one week (Mon-Sun)
        jan1 = date(self._year, 1, 1)
        dec31 = date(self._year, 12, 31)

        # Start from Monday of the week containing Jan 1
        start = jan1 - timedelta(days=jan1.weekday())

        # Collect weeks
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

        # Month labels
        month_labels = Text("     ")
        for week in weeks:
            first_real = next((d for d in week if d), None)
            if first_real and first_real.day <= 7:
                label = first_real.strftime("%b")[:3]
                month_labels.append(label[:2])
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
                    row.append(" ")
                else:
                    total = self._daily.get(d, 0)
                    level = _intensity(total)
                    char = _BLOCK if total > 0 else _EMPTY
                    row.append(char, style=_COLORS[level])
            console.print(row)

        # Legend + stats
        total_year = sum(self._daily.values())
        peak_day = max(self._daily, key=self._daily.get) if self._daily else None

        legend = Text("\n")
        legend.append("░ 0  ", style=_COLORS[0])
        for i in range(1, 5):
            legend.append("█ ", style=_COLORS[i])
        console.print(legend)

        console.print(
            f"Total {self._year}: [green]{total_year:,}[/green] tokens"
            + (f"  |  Peak: [green]{peak_day}[/green] "
               f"({self._daily[peak_day]:,})" if peak_day else "")
        )
        console.print()
