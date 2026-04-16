"""Render top projects as horizontal bars with privacy filtering."""

from cc_stats.formatters import fmt_num
from cc_stats.privacy import redact_project_name
from cc_stats.svg.constants import (
    CARD_WIDTH,
    FONT,
    GREENS,
    LABEL,
    PROJECTS_BAR_MAX_W,
    PROJECTS_Y,
)


def render_project_bars(
    top_projects: list[tuple[str, int]],
    public_repos: set[str],
) -> str:
    if not top_projects:
        return ""

    max_tokens = top_projects[0][1] if top_projects[0][1] > 0 else 1
    lines: list[str] = []

    lines.append(
        f'  <text x="20" y="{PROJECTS_Y - 6}" fill="{LABEL}" font-size="8" '
        f'font-family="{FONT}" letter-spacing="0.05em">TOP PROJECTS BY TOKENS</text>'
    )

    for i, (name, tokens) in enumerate(top_projects[:3]):
        y = PROJECTS_Y + i * 26 + 4
        bar_w = max(12, int(tokens / max_tokens * PROJECTS_BAR_MAX_W))
        opacity = 0.6 - i * 0.12
        display = redact_project_name(name, public_repos)

        lines.append(
            f'  <rect x="20" y="{y}" width="{bar_w}" height="14" '
            f'rx="4" fill="{GREENS[4]}" opacity="{opacity:.2f}"/>'
        )
        lines.append(
            f'  <text x="{bar_w + 30}" y="{y + 11}" fill="{LABEL}" '
            f'font-size="10" font-family="{FONT}">{display}</text>'
        )
        lines.append(
            f'  <text x="{CARD_WIDTH - 20}" y="{y + 11}" fill="{LABEL}" '
            f'font-size="9" font-family="{FONT}" text-anchor="end" '
            f'opacity="0.7">{fmt_num(tokens)} tkns</text>'
        )

    return "\n".join(lines)
