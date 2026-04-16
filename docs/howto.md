# How-to Guides

## How to add multiple Claude accounts

If you use Claude Code under separate accounts (e.g., personal and work), each has its own `.claude` directory. Add an `[[accounts]]` entry for each:

```toml
[[accounts]]
path = "~/.claude"

[[accounts]]
path = "/home/me/.claude-work"
```

Paths support `~` expansion. Each path should point to the root Claude config directory -- the one containing a `projects/` subdirectory with `.jsonl` session files.

cc-stats also counts distinct accounts from the desktop app's session directory (see [Data sources](reference.md#data-sources)). The final account count is `max(desktop_accounts, len(config.account_paths))`.

## How to disable backfill

Backfill fills in the activity grid for dates between your first Claude Code token and today, even on days without session data. This creates a more complete-looking grid but inflates the `active_days` count.

To disable it:

```toml
[general]
backfill = false
```

With backfill off, only days with actual session data appear in the grid. The `active_days` stat reflects real usage.

See [Explanation: What backfill does](explanation.md#what-backfill-does-and-why) for details.

## How to use without the `gh` CLI

The `gh` CLI is used for one thing: fetching your public repo list to decide which project names are safe to display. If `gh` is not installed or not authenticated, cc-stats still works -- it just redacts all project names to `[redacted]` in the SVG.

To run without `gh`:

1. Leave `github_username` empty in the config, or
2. Run normally -- if `gh` is missing, the privacy module returns an empty set and all names are redacted.

No error is raised. The JSON output still contains full project names (it is a local file, not displayed publicly). Only the SVG applies redaction.

If you want project names visible without `gh`, there is currently no override. You would need to provide a working `gh` installation with access to the GitHub API.

## How to embed the card in a GitHub README

The SVG is a static file. Add it to any repo and reference it in Markdown:

```markdown
![Claude Code Stats](./claude-card.svg)
```

For a GitHub profile README (the repo matching your username):

```shell
# From your profile repo
cp /path/to/graph/claude-card.svg .
git add claude-card.svg
git commit -m "update claude code stats"
git push
```

The card is 480x380 pixels, uses the Geist Mono font (loaded from Google Fonts via an `@import` in the SVG), and has a dark background matching GitHub's dark theme.

If the font does not load (e.g., in contexts that block external requests), the card falls back to `monospace`.

## How to automate updates with a local script

Create a script that regenerates the card and commits it:

```shell
#!/usr/bin/env bash
set -euo pipefail

PROFILE_REPO="$HOME/Projects/yourname"

cc-stats generate --out "$PROFILE_REPO"
cd "$PROFILE_REPO"
git add claude-card.svg claude-stats.json
git diff --cached --quiet && exit 0  # nothing changed
git commit -m "update claude code stats"
git push
```

Run it daily with cron:

```shell
crontab -e
```

```
0 9 * * * /path/to/update-stats.sh
```

Or use a launchd plist on macOS, a systemd timer on Linux, or Task Scheduler on Windows.

The script is idempotent -- if no sessions have changed, the generated files are the same and the `git diff --cached --quiet` check skips the commit.
