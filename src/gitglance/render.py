"""Terminal rendering: colors, bars, tables."""

from __future__ import annotations

import os
import sys
from datetime import datetime

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
CYAN = "\x1b[36m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
MAGENTA = "\x1b[35m"
RED = "\x1b[31m"

BAR_CHAR = "█"


def use_color(no_color: bool) -> bool:
    if no_color:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


class Painter:
    def __init__(self, use_color: bool) -> None:
        self.enabled = use_color

    def _wrap(self, code: str, text: str) -> str:
        return f"{code}{text}{RESET}" if self.enabled else text

    def bold(self, text: str) -> str:
        return self._wrap(BOLD, text)

    def dim(self, text: str) -> str:
        return self._wrap(DIM, text)

    def cyan(self, text: str) -> str:
        return self._wrap(CYAN, text)

    def green(self, text: str) -> str:
        return self._wrap(GREEN, text)

    def yellow(self, text: str) -> str:
        return self._wrap(YELLOW, text)

    def magenta(self, text: str) -> str:
        return self._wrap(MAGENTA, text)

    def red(self, text: str) -> str:
        return self._wrap(RED, text)


def bar(paint: Painter, value: int, max_value: int, width: int = 30) -> str:
    if max_value <= 0:
        return paint.dim("·" * width)
    filled = round(value / max_value * width)
    filled_bar = BAR_CHAR * filled
    empty = "░" * (width - filled)
    return paint.green(filled_bar) + paint.dim(empty)


def heatmap(paint: Painter, value: int, max_value: int) -> str:
    if max_value <= 0 or value <= 0:
        return paint.dim("░")
    ratio = value / max_value
    if ratio > 0.75:
        return paint.red("██")
    if ratio > 0.5:
        return paint.yellow("▓")
    if ratio > 0.25:
        return paint.green("▒")
    return paint.cyan("░")


def fmt_date(dt: datetime | None) -> str:
    if dt is None:
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M")


def relative_days(dt: datetime | None) -> str:
    if dt is None:
        return "-"
    now = datetime.now(dt.tzinfo or None)
    days = (now - dt).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def fmt_number(value: int) -> str:
    return f"{value:,}".replace(",", "_")
