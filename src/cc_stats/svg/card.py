"""Assemble the full SVG card from component renderers."""

from cc_stats.aggregator import Stats
from cc_stats.svg.constants import (
    BG,
    BORDER,
    CARD_HEIGHT,
    CARD_RADIUS,
    CARD_WIDTH,
    FONT,
    FONT_IMPORT,
    LABEL,
    VALUE,
)
from cc_stats.svg.grid import render_contribution_grid
from cc_stats.svg.project_bars import render_project_bars
from cc_stats.svg.stat_boxes import render_stat_boxes


def render_card(stats: Stats, public_repos: set[str]) -> str:
    """Render the complete SVG card."""
    stat_boxes = render_stat_boxes(stats)
    grid = render_contribution_grid(stats.daily)
    projects = render_project_bars(stats.top_projects, public_repos)

    acct = stats.accounts
    subtitle = (
        f'{stats.active_days} active days  \u00b7  '
        f'{acct} account{"s" if acct > 1 else ""}'
    )

    return f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}">
  <defs>
    <style>@import url('{FONT_IMPORT}');</style>
  </defs>

  <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="{CARD_RADIUS}" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>

  <text x="20" y="34" fill="{VALUE}" font-size="14" font-family="{FONT}" font-weight="600">claude code</text>
  <text x="20" y="50" fill="{LABEL}" font-size="9" font-family="{FONT}">{subtitle}</text>

{stat_boxes}

  <text x="20" y="188" fill="{LABEL}" font-size="8" font-family="{FONT}" letter-spacing="0.05em">ACTIVITY</text>
{grid}

{projects}
</svg>"""
