from __future__ import annotations

from datetime import date, timedelta

from rich.console import Console
from rich.text import Text

from token_garden.providers.base import DailyUsage

_COLORS = [
    "#161b22",  # 0: empty
    "#0e4429",  # 1: dark green
    "#006d32",  # 2: medium green
    "#26a641",  # 3: green
    "#39d353",  # 4: bright green
]

_BLOCK = "█"
_EMPTY = "░"


def _compute_thresholds(values: list[int]) -> list[int]:
    """Compute 4 intensity thresholds from actual usage data (percentile-based)."""
    if not values:
        return [1, 10_000, 50_000, 100_000]
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return [
        sorted_vals[max(0, int(n * 0.25) - 1)],
        sorted_vals[max(0, int(n * 0.50) - 1)],
        sorted_vals[max(0, int(n * 0.75) - 1)],
        sorted_vals[-1],
    ]


def _intensity(total: int, thresholds: list[int]) -> int:
    if total <= 0:
        return 0
    for level in range(4, 0, -1):
        if total >= thresholds[level - 1]:
            return level
    return 1


class GridView:
    def __init__(self, records: list[DailyUsage], year: int):
        self._year = year
        self._daily: dict[date, int] = {}
        for r in records:
            self._daily[r.date] = self._daily.get(r.date, 0) + r.total_tokens
        active = [v for v in self._daily.values() if v > 0]
        self._thresholds = _compute_thresholds(active)

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

        # Month labels — 1 char per week to match grid width
        month_labels = Text("     ")
        for week in weeks:
            first_real = next((d for d in week if d), None)
            if first_real and first_real.day <= 7:
                month_labels.append(first_real.strftime("%b")[0])
            else:
                month_labels.append(" ")
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
                    level = _intensity(total, self._thresholds)
                    char = _BLOCK if total > 0 else _EMPTY
                    row.append(char, style=_COLORS[level])
            console.print(row)

        total_year = sum(self._daily.values())
        peak_day = max(self._daily, key=self._daily.get) if self._daily else None
        t = self._thresholds

        legend = Text("\n")
        legend.append("░ 0  ", style=_COLORS[0])
        legend.append(f"█ 1-{t[0]:,}  ", style=_COLORS[1])
        legend.append(f"█ -{t[1]:,}  ", style=_COLORS[2])
        legend.append(f"█ -{t[2]:,}  ", style=_COLORS[3])
        legend.append(f"█ {t[2]+1:,}+", style=_COLORS[4])
        console.print(legend)

        console.print(
            f"Total {self._year}: [green]{total_year:,}[/green] tokens"
            + (f"  |  Peak: [green]{peak_day}[/green] "
               f"({self._daily[peak_day]:,})" if peak_day else "")
        )
        console.print()
