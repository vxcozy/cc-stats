# Reference

## CLI

Entry point: `cc-stats` (defined in `src/cc_stats/cli.py`).

### `cc-stats init`

Create a `cc-stats.toml` template in the target directory.

```
cc-stats init [--dest DIR]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--dest` | `.` | Directory to write `cc-stats.toml` |

Exits with code 1 if the file already exists.

### `cc-stats generate`

Parse session data, compute stats, write JSON and SVG.

```
cc-stats generate [--config PATH] [--out DIR]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--config` | Auto-detect | Path to `cc-stats.toml` |
| `--out` | `.` | Output directory for `claude-stats.json` and `claude-card.svg` |

Config auto-detection searches these paths in order:

1. `./cc-stats.toml`
2. `~/.config/cc-stats/config.toml`

If neither exists, defaults are used (no GitHub username, backfill enabled, single account at `~/.claude`).

### `cc-stats --version`

Print the version string and exit.

---

## Config file format

File: `cc-stats.toml` (TOML syntax). Defined in `src/cc_stats/config.py`.

### `[general]`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `github_username` | string | `""` | GitHub username for privacy filtering. Used to fetch public repo list via `gh api`. |
| `backfill` | bool | `true` | Fill activity grid with placeholder entries for days between first token date and today. |

### `[[accounts]]`

Repeatable table. Each entry specifies a Claude config directory.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Path to a `.claude` directory. Supports `~` expansion. |

If no `[[accounts]]` entries are present (or none have a `path` key), defaults to `[~/.claude]`.

### Example

```toml
[general]
github_username = "alice"
backfill = true

[[accounts]]
path = "~/.claude"

[[accounts]]
path = "/opt/claude-ci/.claude"
```

---

## Output files

### `claude-stats.json`

JSON object with this structure:

```json
{
  "generated": "2025-06-15T12:00:00+00:00",
  "accounts": 1,
  "summary": {
    "total_sessions": 342,
    "total_messages": 2841,
    "total_tokens": 18420000,
    "active_days": 89,
    "current_streak": 12,
    "longest_streak": 34,
    "peak_hour": 14,
    "favorite_model": "claude-sonnet-4-20250514"
  },
  "daily": {
    "2025-06-01": {
      "sessions": 5,
      "user_msgs": 42,
      "assistant_msgs": 42,
      "input_tokens": 120000,
      "output_tokens": 45000,
      "minutes": 83.2
    }
  },
  "top_projects": [
    { "name": "myapp", "tokens": 5200000 }
  ]
}
```

Field details:

| Field | Type | Description |
|-------|------|-------------|
| `generated` | string | ISO 8601 UTC timestamp of generation |
| `accounts` | int | Number of Claude accounts detected |
| `summary.total_sessions` | int | Total sessions (excludes backfilled) |
| `summary.total_messages` | int | User + assistant messages |
| `summary.total_tokens` | int | Input + output tokens |
| `summary.active_days` | int | Days with any activity (includes backfilled if enabled) |
| `summary.current_streak` | int | Consecutive days ending today (or yesterday) |
| `summary.longest_streak` | int | Longest consecutive-day run |
| `summary.peak_hour` | int | 0-23 hour with most activity |
| `summary.favorite_model` | string | Model ID with the highest message count |
| `daily` | object | Per-day stats keyed by `YYYY-MM-DD`. Backfilled days are excluded from JSON. |
| `top_projects` | array | Up to 3 projects sorted by total token count (input + output) |

### `claude-card.svg`

A 480x380 SVG card. Structure (from `src/cc_stats/svg/`):

- **Header**: title ("claude code") and subtitle (active days, account count)
- **Stat boxes**: 2 rows of 4 boxes each. Row 1: Sessions, Messages, Total tokens, Active days. Row 2: Current streak, Longest streak, Peak hour, Favorite model.
- **Activity grid**: 26-column contribution heatmap (about 6 months). Green intensity scales with session count per day.
- **Top projects**: up to 3 horizontal bars with token counts. Project names are privacy-filtered.

Styling constants are in `src/cc_stats/svg/constants.py`:

| Constant | Value | Description |
|----------|-------|-------------|
| `CARD_WIDTH` | 480 | SVG width in px |
| `CARD_HEIGHT` | 380 | SVG height in px |
| `BG` | `#0d1117` | Background color (GitHub dark theme) |
| `BORDER` | `#30363d` | Border and box stroke color |
| `LABEL` | `#8b949e` | Label text color (4.7:1 contrast vs BG) |
| `VALUE` | `#e6edf3` | Value text color (13.5:1 contrast vs BG) |
| `GREENS` | 5-level scale | Activity grid colors, from empty to max |
| `FONT` | Geist Mono | Loaded via Google Fonts `@import` in the SVG `<defs>` |

---

## Data sources

### JSONL session files

Location: `<account_path>/projects/<encoded_project_dir>/<session_id>.jsonl`

Parsed by `src/cc_stats/parsers/jsonl.py`. Each `.jsonl` file is one session. Lines are JSON objects with a `type` field (`"user"` or `"assistant"`).

From assistant messages, the parser extracts:
- `message.usage.input_tokens`
- `message.usage.cache_creation_input_tokens`
- `message.usage.cache_read_input_tokens`
- `message.usage.output_tokens`
- `message.model`

Timestamps come from the `timestamp` field on each line (ISO 8601). The session's day is the date of the earliest timestamp.

Files under `subagents/` directories are skipped.

### Desktop app metadata

Location (platform-dependent):
- macOS: `~/Library/Application Support/Claude/claude-code-sessions/<account_id>/<session_dir>/*.json`
- Linux: `~/.config/Claude/claude-code-sessions/<account_id>/<session_dir>/*.json`
- Windows: `%APPDATA%/Claude/claude-code-sessions/<account_id>/<session_dir>/*.json`

Parsed by `src/cc_stats/parsers/desktop.py`. Each JSON file contains metadata for one session:

| Field | Used for |
|-------|----------|
| `cliSessionId` | Deduplication key |
| `createdAt` | Session start (epoch ms) |
| `lastActivityAt` | Session end (epoch ms) |
| `model` | Model tracking |
| `completedTurns` | Message count (used for both user and assistant) |
| `originCwd` / `cwd` | Project name resolution |

Desktop metadata has no token counts. When a session exists in both JSONL and desktop sources, the JSONL version is kept (it has richer data).

### First token date

Read from `<account_path>/backups/.claude.json.backup.*` or `<account_path>/.claude.json`. The `claudeCodeFirstTokenDate` field (legacy) or `firstStartTime` (current) is used as the start date for backfill. With multiple `[[accounts]]`, the earliest date across all accounts wins. If neither key is present in any account's config, backfill falls back to the earliest real session date.

---

## Privacy model

Defined in `src/cc_stats/privacy.py`.

1. If `github_username` is set, cc-stats calls `gh api users/{username}/repos --jq '.[].name' --paginate` with a 10-second timeout.
2. The returned repo names form the allow-list.
3. Each project name in the SVG is checked against this list (case-insensitive). Matches are shown; non-matches render as `[redacted]`.
4. If `github_username` is empty, `gh` is missing, or the API call fails, the allow-list is empty and all project names are redacted.

The JSON output is not filtered -- it contains the real project names. Only the SVG applies redaction.
