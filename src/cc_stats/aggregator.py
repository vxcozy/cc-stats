"""Merge sessions from all sources, deduplicate, compute daily stats and streaks."""

import glob
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cc_stats.parsers import SessionData


@dataclass
class DailyBucket:
    sessions: int = 0
    user_msgs: int = 0
    assistant_msgs: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    minutes: float = 0.0
    backfilled: bool = False


@dataclass
class Stats:
    """Aggregated stats ready for rendering."""

    generated: str = ""
    accounts: int = 1
    total_sessions: int = 0
    total_messages: int = 0
    total_tokens: int = 0
    active_days: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    peak_hour: int = 0
    favorite_model: str = "n/a"
    daily: dict[str, DailyBucket] = field(default_factory=dict)
    top_projects: list[tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize for JSON output. Omits backfill flag from daily data."""
        return {
            "generated": self.generated,
            "accounts": self.accounts,
            "summary": {
                "total_sessions": self.total_sessions,
                "total_messages": self.total_messages,
                "total_tokens": self.total_tokens,
                "active_days": self.active_days,
                "current_streak": self.current_streak,
                "longest_streak": self.longest_streak,
                "peak_hour": self.peak_hour,
                "favorite_model": self.favorite_model,
            },
            "daily": {
                day: {
                    "sessions": b.sessions,
                    "user_msgs": b.user_msgs,
                    "assistant_msgs": b.assistant_msgs,
                    "input_tokens": b.input_tokens,
                    "output_tokens": b.output_tokens,
                    "minutes": round(b.minutes, 1),
                }
                for day, b in sorted(self.daily.items())
                if not b.backfilled
            },
            "top_projects": [
                {"name": name, "tokens": tokens}
                for name, tokens in self.top_projects
            ],
        }


def aggregate(
    jsonl_sessions: list[SessionData],
    desktop_sessions: list[SessionData],
    *,
    accounts: int = 1,
    backfill: bool = True,
    first_token_date: str | None = None,
) -> Stats:
    """Merge all sessions, deduplicate, bucket by day, compute summary stats."""
    # Deduplicate: JSONL data wins over desktop metadata
    sessions_by_id: dict[str, SessionData] = {}
    for s in jsonl_sessions:
        sessions_by_id[s.cli_session_id] = s
    for s in desktop_sessions:
        if s.cli_session_id not in sessions_by_id:
            sessions_by_id[s.cli_session_id] = s

    # Aggregate into daily buckets
    daily: dict[str, DailyBucket] = defaultdict(DailyBucket)
    models: dict[str, int] = defaultdict(int)
    hours: dict[int, int] = defaultdict(int)
    project_tokens: dict[str, int] = defaultdict(int)

    for session in sessions_by_id.values():
        day = session.day
        bucket = daily[day]
        bucket.sessions += 1
        bucket.user_msgs += session.user_msgs
        bucket.assistant_msgs += session.assistant_msgs
        bucket.input_tokens += session.input_tokens
        bucket.output_tokens += session.output_tokens
        bucket.minutes += session.duration_min

        for model, count in session.models.items():
            models[model] += count
        for hour, count in session.hours.items():
            hours[hour] += count
        project_tokens[session.project] += session.input_tokens + session.output_tokens

    # Backfill from first token date to today
    all_days = set(daily.keys())
    if backfill and first_token_date:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = first_token_date
        while cursor <= today:
            if cursor not in all_days:
                all_days.add(cursor)
                daily[cursor] = DailyBucket(sessions=1, backfilled=True)
            cursor = (_parse_day(cursor) + timedelta(days=1)).strftime("%Y-%m-%d")

    # Compute summary
    current_streak, longest_streak = compute_streaks(sorted(all_days))
    real_buckets = [b for b in daily.values() if not b.backfilled]
    total_sessions = sum(b.sessions for b in real_buckets)
    total_messages = sum(b.user_msgs + b.assistant_msgs for b in real_buckets)
    total_tokens = sum(b.input_tokens + b.output_tokens for b in real_buckets)
    peak_hour = max(hours, key=hours.get) if hours else 0
    favorite_model = max(models, key=models.get) if models else "n/a"
    top_projects = sorted(project_tokens.items(), key=lambda x: -x[1])[:3]

    return Stats(
        generated=datetime.now(timezone.utc).isoformat(),
        accounts=accounts,
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_tokens=total_tokens,
        active_days=len(all_days),
        current_streak=current_streak,
        longest_streak=longest_streak,
        peak_hour=peak_hour,
        favorite_model=favorite_model,
        daily=dict(daily),
        top_projects=top_projects,
    )


def compute_streaks(sorted_days: list[str]) -> tuple[int, int]:
    """Compute current and longest streaks from a sorted list of date strings."""
    if not sorted_days:
        return 0, 0

    longest = streak = 1
    for i in range(1, len(sorted_days)):
        prev = _parse_day(sorted_days[i - 1])
        curr = _parse_day(sorted_days[i])
        if (curr - prev).days == 1:
            streak += 1
        else:
            longest = max(longest, streak)
            streak = 1
    longest = max(longest, streak)

    # Current streak: count backwards from most recent day
    today = datetime.now().strftime("%Y-%m-%d")
    gap = (_parse_day(today) - _parse_day(sorted_days[-1])).days
    if gap > 1:
        return 0, longest

    current = 1
    for i in range(len(sorted_days) - 2, -1, -1):
        prev = _parse_day(sorted_days[i])
        curr = _parse_day(sorted_days[i + 1])
        if (curr - prev).days == 1:
            current += 1
        else:
            break

    return current, longest


def get_first_token_date(claude_dirs: list[Path]) -> str | None:
    """Read claudeCodeFirstTokenDate from Claude config backups."""
    for claude_dir in claude_dirs:
        # Try backups first (most reliable), then main config
        backup_pattern = str(claude_dir / "backups" / ".claude.json.backup.*")
        candidates = sorted(glob.glob(backup_pattern))
        if not candidates:
            main_config = claude_dir / ".claude.json"
            if main_config.is_file():
                candidates = [str(main_config)]

        for path in candidates[:1]:
            try:
                with open(path) as f:
                    data = json.load(f)
                date_str = data.get("claudeCodeFirstTokenDate", "")
                if date_str:
                    return date_str[:10]
            except (json.JSONDecodeError, OSError):
                continue
    return None


def _parse_day(day_str: str) -> datetime:
    return datetime.strptime(day_str, "%Y-%m-%d")
