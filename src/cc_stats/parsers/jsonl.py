"""Parse Claude Code session JSONL files from ~/.claude/projects/."""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from cc_stats.parsers import SessionData
from cc_stats.paths import resolve_project_name


def parse_session(jsonl_path: Path) -> SessionData | None:
    """Parse a single session JSONL file into normalized metrics."""
    user_msgs = 0
    assistant_msgs = 0
    input_tokens = 0
    output_tokens = 0
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    models: dict[str, int] = defaultdict(int)
    hours: dict[int, int] = defaultdict(int)

    try:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = entry.get("type", "")
                if msg_type == "user":
                    user_msgs += 1
                elif msg_type == "assistant":
                    assistant_msgs += 1
                    msg = entry.get("message")
                    if isinstance(msg, dict):
                        usage = msg.get("usage", {})
                        input_tokens += usage.get("input_tokens", 0)
                        input_tokens += usage.get("cache_creation_input_tokens", 0)
                        input_tokens += usage.get("cache_read_input_tokens", 0)
                        output_tokens += usage.get("output_tokens", 0)
                        model = msg.get("model", "")
                        if model:
                            models[model] += 1

                ts_raw = entry.get("timestamp")
                if not isinstance(ts_raw, str):
                    continue
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except ValueError:
                    continue

                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts
                hours[ts.hour] += 1
    except OSError:
        return None

    if first_ts is None:
        return None

    duration = (last_ts - first_ts).total_seconds() / 60 if last_ts else 0.0
    project = resolve_project_name(jsonl_path.parent.name)

    return SessionData(
        cli_session_id=jsonl_path.stem,
        source="jsonl",
        user_msgs=user_msgs,
        assistant_msgs=assistant_msgs,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_min=duration,
        day=first_ts.strftime("%Y-%m-%d"),
        models=dict(models),
        hours=dict(hours),
        project=project,
    )


def parse_all(claude_dirs: list[Path]) -> list[SessionData]:
    """Parse all session JSONL files across the given Claude config directories."""
    sessions: list[SessionData] = []
    for claude_dir in claude_dirs:
        projects_dir = claude_dir / "projects"
        if not projects_dir.is_dir():
            continue
        for jsonl_path in projects_dir.glob("*/*.jsonl"):
            if "subagents" in str(jsonl_path):
                continue
            session = parse_session(jsonl_path)
            if session is not None:
                sessions.append(session)
    return sessions
