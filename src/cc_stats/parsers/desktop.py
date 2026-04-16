"""Parse desktop app session metadata for all Claude accounts."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from cc_stats.parsers import SessionData
from cc_stats.paths import desktop_session_dir


def parse_session(meta_path: Path) -> SessionData | None:
    """Parse a single desktop session metadata JSON file."""
    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    cli_id = meta.get("cliSessionId", "")
    created = meta.get("createdAt", 0)
    last_activity = meta.get("lastActivityAt", created)
    model = meta.get("model", "")
    turns = meta.get("completedTurns", 0)

    if not created or not cli_id:
        return None

    created_dt = datetime.fromtimestamp(created / 1000, tz=timezone.utc)
    last_dt = datetime.fromtimestamp(last_activity / 1000, tz=timezone.utc)
    duration = max((last_dt - created_dt).total_seconds() / 60, 0.0)

    # Resolve project from originCwd (safer than cwd for worktrees)
    origin_cwd = meta.get("originCwd", meta.get("cwd", ""))
    project = os.path.basename(origin_cwd.rstrip("/")) if origin_cwd else "misc"

    return SessionData(
        cli_session_id=cli_id,
        source="desktop_meta",
        user_msgs=turns,
        assistant_msgs=turns,
        input_tokens=0,
        output_tokens=0,
        duration_min=duration,
        day=created_dt.strftime("%Y-%m-%d"),
        models={model: turns} if model else {},
        hours={created_dt.hour: 1},
        project=project,
    )


def parse_all() -> list[SessionData]:
    """Parse all desktop session metadata files across all accounts."""
    base = desktop_session_dir()
    if base is None:
        return []

    sessions: list[SessionData] = []
    seen_ids: set[str] = set()

    for meta_path in base.glob("*/*/*.json"):
        session = parse_session(meta_path)
        if session is None:
            continue
        if session.cli_session_id in seen_ids:
            continue
        seen_ids.add(session.cli_session_id)
        sessions.append(session)

    return sessions


def count_accounts() -> int:
    """Count distinct Claude accounts from the desktop app session directory."""
    base = desktop_session_dir()
    if base is None:
        return 0
    return len([
        d for d in base.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])
