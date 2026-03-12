from __future__ import annotations

from datetime import date

from rich.console import Console
from rich.text import Text

from token_garden.providers.base import DailyUsage

_PLANT_THRESHOLDS = [
    (200_000, "🌴"),
    (100_000, "🌳"),
    (50_000,  "🌲"),
    (10_000,  "🌿"),
    (1,       "🌱"),
    (0,       " "),
]

_COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#39d353",
]


def _plant_emoji(weekly_total: int) -> str:
    for threshold, emoji in _PLANT_THRESHOLDS:
        if weekly_total >= threshold:
            return emoji
    return " "


def _week_number(d: date) -> int:
    return d.isocalendar()[1]


class GardenView:
    def __init__(self, records: list[DailyUsage], year: int):
        self._year = year
        # Aggregate by ISO week number
        self._weekly: dict[int, int] = {}
        for r in records:
            if r.date.year != year:
                continue
            wk = _week_number(r.date)
            self._weekly[wk] = self._weekly.get(wk, 0) + r.total_tokens

    def render(self, console: Console | None = None) -> None:
        if console is None:
            console = Console()

        console.print(f"\n[bold green]🌿 Token Garden — {self._year}[/bold green]")
        console.print("[dim]주별 토큰 사용량으로 식물이 자라요[/dim]\n")

        max_tokens = max(self._weekly.values(), default=1)

        for wk in range(1, 53):
            total = self._weekly.get(wk, 0)
            emoji = _plant_emoji(total)
            bar_len = int((total / max_tokens) * 30) if max_tokens > 0 else 0
            bar = "█" * bar_len
            color = "#39d353" if total >= 200_000 else \
                    "#26a641" if total >= 100_000 else \
                    "#006d32" if total >= 50_000 else \
                    "#0e4429" if total >= 10_000 else \
                    "#161b22"

            line = Text(f"w{wk:02d}  {emoji}  ")
            line.append(bar, style=color)
            line.append(f"  {total:>10,}" if total else "")
            console.print(line)

        total_year = sum(self._weekly.values())
        peak_week = max(self._weekly, key=self._weekly.get) if self._weekly else None

        console.print(
            f"\nTotal {self._year}: [green]{total_year:,}[/green] tokens"
            + (f"  |  Peak: [green]w{peak_week:02d}[/green] "
               f"({self._weekly[peak_week]:,})" if peak_week else "")
        )
        console.print()
