"""Render the 2x4 stat box grid."""

from cc_stats.aggregator import Stats
from cc_stats.formatters import fmt_hour, fmt_num
from cc_stats.svg.constants import (
    BORDER,
    BOX_GAP,
    BOX_HEIGHT,
    BOX_RADIUS,
    BOX_ROW1_Y,
    BOX_ROW2_Y,
    BOX_WIDTH,
    BOX_X,
    CELL_EMPTY,
    FONT,
    LABEL,
    VALUE,
)


def render_stat_boxes(stats: Stats) -> str:
    rows: list[list[tuple[str, str]]] = [
        [
            ("Sessions", fmt_num(stats.total_sessions)),
            ("Messages", fmt_num(stats.total_messages)),
            ("Total tokens", fmt_num(stats.total_tokens)),
            ("Active days", str(stats.active_days)),
        ],
        [
            ("Current streak", f"{stats.current_streak}d"),
            ("Longest streak", f"{stats.longest_streak}d"),
            ("Peak hour", fmt_hour(stats.peak_hour)),
            ("Favorite model", stats.favorite_model.replace("claude-", "")),
        ],
    ]

    lines: list[str] = []
    for row_data, y in [(rows[0], BOX_ROW1_Y), (rows[1], BOX_ROW2_Y)]:
        for i, (label, value) in enumerate(row_data):
            x = BOX_X + i * (BOX_WIDTH + BOX_GAP)
            font_size = 14 if len(value) > 8 else 16

            lines.append(
                f'  <rect x="{x}" y="{y}" width="{BOX_WIDTH}" height="{BOX_HEIGHT}" '
                f'rx="{BOX_RADIUS}" fill="{CELL_EMPTY}" stroke="{BORDER}" stroke-width="0.5"/>'
            )
            lines.append(
                f'  <text x="{x + 10}" y="{y + 18}" fill="{LABEL}" '
                f'font-size="8" font-family="{FONT}" letter-spacing="0.02em">{label}</text>'
            )
            lines.append(
                f'  <text x="{x + 10}" y="{y + 40}" fill="{VALUE}" '
                f'font-size="{font_size}" font-family="{FONT}" font-weight="600">{value}</text>'
            )

    return "\n".join(lines)
