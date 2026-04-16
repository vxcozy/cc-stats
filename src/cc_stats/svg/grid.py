"""Render the contribution heatmap grid."""

from datetime import datetime, timedelta

from cc_stats.aggregator import DailyBucket
from cc_stats.svg.constants import CELL_EMPTY, GREENS, GRID_CELL, GRID_COLUMNS, GRID_GAP, GRID_X, GRID_Y


def render_contribution_grid(daily: dict[str, DailyBucket]) -> str:
    today = datetime.now()

    # Map days to session counts (for color intensity)
    counts_by_day: dict[str, int] = {}
    for day, bucket in daily.items():
        counts_by_day[day] = bucket.sessions

    max_count = max(counts_by_day.values(), default=1)
    lines: list[str] = []

    # Align grid to week boundaries, ending on today
    days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    grid_start = today - timedelta(days=GRID_COLUMNS * 7 - 1 + days_since_sunday)

    for week in range(GRID_COLUMNS):
        for dow in range(7):
            day = grid_start + timedelta(days=week * 7 + dow)
            if day > today:
                continue

            x = GRID_X + week * (GRID_CELL + GRID_GAP)
            y = GRID_Y + dow * (GRID_CELL + GRID_GAP)
            count = counts_by_day.get(day.strftime("%Y-%m-%d"), 0)
            color = _color_for_count(count, max_count)

            lines.append(
                f'  <rect x="{x}" y="{y}" width="{GRID_CELL}" height="{GRID_CELL}" '
                f'rx="2" fill="{color}"/>'
            )

    return "\n".join(lines)


def _color_for_count(count: int, max_count: int) -> str:
    if count == 0:
        return CELL_EMPTY
    pct = count / max_count
    if pct <= 0.25:
        return GREENS[1]
    if pct <= 0.50:
        return GREENS[2]
    if pct <= 0.75:
        return GREENS[3]
    return GREENS[4]
