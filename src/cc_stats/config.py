"""TOML config loading with sensible defaults."""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    github_username: str = ""
    backfill: bool = True
    account_paths: list[Path] = field(default_factory=lambda: [Path.home() / ".claude"])


CONFIG_SEARCH_PATHS = [
    "cc-stats.toml",
    os.path.expanduser("~/.config/cc-stats/config.toml"),
]


def load_config(path: str | None = None) -> Config:
    """Load config from TOML file. Falls back to defaults if not found."""
    if path is not None:
        p = Path(path)
        if p.is_file():
            return _parse_file(p)
        return Config()

    for candidate in CONFIG_SEARCH_PATHS:
        p = Path(candidate)
        if p.is_file():
            return _parse_file(p)

    return Config()


def _parse_file(path: Path) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    general = raw.get("general", {})
    accounts_raw = raw.get("accounts", [])

    account_paths = [
        Path(os.path.expanduser(a["path"]))
        for a in accounts_raw
        if "path" in a
    ]
    if not account_paths:
        account_paths = [Path.home() / ".claude"]

    return Config(
        github_username=general.get("github_username", ""),
        backfill=general.get("backfill", True),
        account_paths=account_paths,
    )


def generate_template() -> str:
    return """\
# cc-stats configuration
# https://github.com/vxcozy/cc-stats

[general]
github_username = ""    # your GitHub username (for privacy filtering)
backfill = true         # fill activity grid for days with no local data

# Add one or more Claude Code accounts.
# Each account points to a Claude config directory.

[[accounts]]
path = "~/.claude"

# [[accounts]]
# path = "/path/to/other/.claude"
"""
