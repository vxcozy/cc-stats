# Explanation

## How session data is discovered and merged

cc-stats reads session data from two independent sources:

1. **JSONL files** in `<account_path>/projects/`. Each `.jsonl` file represents one Claude Code session and contains the full message log with token usage, model info, and timestamps.

2. **Desktop app metadata** from a platform-specific directory (e.g., `~/Library/Application Support/Claude/claude-code-sessions/` on macOS). These are JSON files with summary metadata: turn count, model, timestamps, working directory. They lack token-level detail.

The merge happens in `src/cc_stats/aggregator.py`:

- All JSONL sessions are indexed by `cli_session_id` (the filename stem).
- Desktop sessions are added only if their `cliSessionId` is not already present from JSONL.

This means the two sources are deduplicated by session ID. A session that exists in both JSONL and desktop metadata is represented exactly once, using the JSONL data.

## Why JSONL data takes precedence over desktop metadata

JSONL files are the authoritative source because they contain per-message detail:

- Exact token counts (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`)
- Model ID per assistant response
- Timestamps per message (allows hour-of-day bucketing and duration calculation)

Desktop metadata only has summary-level data:

- `completedTurns` (a single integer, used as both user and assistant message count)
- One `model` field per session
- `createdAt` and `lastActivityAt` (two timestamps total)
- Zero token information

When both sources have data for the same session, keeping the JSONL version preserves accuracy. Desktop metadata fills gaps for sessions where the JSONL file was deleted or never existed (e.g., sessions that ran only through the desktop app).

## What backfill does and why

The activity grid on the SVG card shows 26 weeks of history. Without backfill, days with no session data show as empty cells.

When `backfill = true` (the default), cc-stats:

1. Reads `claudeCodeFirstTokenDate` from the Claude config backup files. This is the date you first used Claude Code.
2. For every date between that first token date and today, if no session exists, it inserts a placeholder bucket with `sessions=1` and `backfilled=True`.

The effect: the activity grid shows a filled-in history from your first use, rather than scattered dots. This is cosmetic -- the placeholder data is not included in the JSON output or in summary stats like `total_sessions` or `total_messages`. Only `active_days` is affected, since it counts all days including backfilled ones.

If `backfill = false`, only days with real session data appear.

## How project names are resolved

Claude Code stores session JSONL files in directories named after the project path, with slashes replaced by dashes. For example:

```
~/.claude/projects/-Users-alice-Projects-myapp/abc123.jsonl
```

The resolution logic is in `src/cc_stats/paths.py` (`resolve_project_name`):

1. **Strip worktree suffixes.** Everything after the first `--` is dropped. `-Users-alice-Projects-myapp--claude-worktrees-foo` becomes `-Users-alice-Projects-myapp`.

2. **Strip the encoded home directory prefix.** The user's home path (e.g., `-Users-alice`) is removed from the front.

3. **Try filesystem resolution.** The remaining segments are recombined with `/` separators, and the code checks which combinations correspond to real paths on disk. This handles project names with hyphens (e.g., `my-app` is encoded identically to a path segment boundary).

4. **Fallback.** If no real path matches, take the last non-empty segment. Duplicated names like `tome-tome` are collapsed to `tome`.

For desktop metadata, project names come from `originCwd` (or `cwd`), which is a plain filesystem path. `os.path.basename()` extracts the project name directly.

## How privacy filtering works

The SVG card displays up to 3 top projects by token count. Since some of these may be private repos, cc-stats applies privacy filtering before rendering.

The filtering pipeline:

1. `src/cc_stats/privacy.py` calls `gh api users/{username}/repos` to get a list of public repo names.
2. For each project in the top 3, `redact_project_name()` does a case-insensitive comparison against the public repo set.
3. If the project name matches a public repo, it is shown. Otherwise, it renders as `[redacted]`.

Edge cases:

- **`gh` not installed**: the API call raises `FileNotFoundError`, caught silently. All names are redacted.
- **`gh` not authenticated**: the API returns an error. All names are redacted.
- **API timeout**: 10-second timeout. If exceeded, all names are redacted.
- **Empty `github_username`**: the function returns early with an empty set. All names are redacted.

The JSON output (`claude-stats.json`) is not filtered. It always contains the real project names. This file is local and not meant for public display.
