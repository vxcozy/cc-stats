"""Cross-platform Claude data directory discovery and project name resolution."""

import os
import platform
from functools import lru_cache
from pathlib import Path


def desktop_session_dir() -> Path | None:
    """Return the platform-specific desktop app session directory, or None."""
    system = platform.system()
    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code-sessions"
    elif system == "Linux":
        base = Path.home() / ".config" / "Claude" / "claude-code-sessions"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            return None
        base = Path(appdata) / "Claude" / "claude-code-sessions"
    else:
        return None
    return base if base.is_dir() else None


@lru_cache(maxsize=256)
def resolve_project_name(encoded_dir: str) -> str:
    """Resolve a clean project name from Claude's encoded project directory name.

    Claude encodes absolute paths as directory names by replacing '/' with '-'.
    Worktree suffixes appear after '--'. Example:
        -Users-alice-Projects-myapp--claude-worktrees-foo  →  myapp
    """
    name = encoded_dir

    # Strip worktree / tool suffixes (everything after first --)
    if "--" in name:
        name = name.split("--")[0]

    # Strip the encoded home directory prefix
    home_encoded = _encoded_home()
    if home_encoded and name.startswith(home_encoded):
        name = name[len(home_encoded):]

    # Strip leading separator
    name = name.lstrip("-")

    if not name:
        return "misc"

    # Try to resolve to a real path for accurate basename extraction
    resolved = _try_resolve_path(name)
    if resolved:
        return resolved

    # Fallback: take the last meaningful segment
    return _fallback_name(name)


def _encoded_home() -> str:
    """Return the user's home directory encoded as Claude does it."""
    home = str(Path.home())
    return home.replace("/", "-").replace("\\", "-")


def _try_resolve_path(encoded_remainder: str) -> str | None:
    """Attempt to reconstruct the original filesystem path and return its basename.

    Splits on '-' and greedily joins segments with '/' to find the longest
    valid path prefix, then returns os.path.basename of the deepest match.
    """
    home = str(Path.home())
    segments = encoded_remainder.split("-")

    # Try progressively longer path reconstructions
    best_basename: str | None = None
    for i in range(len(segments), 0, -1):
        candidate = os.path.join(home, *segments[:i])
        if os.path.exists(candidate):
            best_basename = os.path.basename(candidate)
            break

    # If direct segment joining fails, try combining adjacent segments with hyphens
    # (handles project names like "my-app" encoded as ...-my-app-...)
    if best_basename is None:
        for split_point in range(len(segments) - 1, 0, -1):
            prefix_path = os.path.join(home, *segments[:split_point])
            suffix = "-".join(segments[split_point:])
            full = os.path.join(prefix_path, suffix)
            if os.path.exists(full):
                best_basename = suffix
                break
            # Also try the suffix as the direct child
            candidate = os.path.join(home, *segments[:split_point])
            if os.path.isdir(candidate):
                child = "-".join(segments[split_point:])
                child_path = os.path.join(candidate, child)
                if os.path.exists(child_path):
                    best_basename = child
                    break

    return best_basename


def _fallback_name(encoded: str) -> str:
    """Extract a reasonable project name when filesystem resolution fails."""
    segments = encoded.split("-")

    # Handle duplicated names: "tome-tome" → "tome"
    half = len(segments) // 2
    if half > 0 and segments[:half] == segments[half:]:
        return "-".join(segments[:half])

    # Take the last non-empty segment
    for segment in reversed(segments):
        if segment:
            return segment

    return "misc"
