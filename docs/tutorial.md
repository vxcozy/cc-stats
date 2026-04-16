# Getting Started

This walks through installing cc-stats, generating your first card, and embedding it in your GitHub profile.

## Prerequisites

- Python 3.11 or later
- Claude Code installed (the tool reads its local session data)
- `gh` CLI authenticated (optional -- needed for project name privacy filtering)

## 1. Install

```shell
pip install cc-stats
```

Verify:

```shell
cc-stats --version
```

```
cc-stats 0.1.0
```

## 2. Create a config file

```shell
cc-stats init
```

This writes `cc-stats.toml` in the current directory:

```toml
# cc-stats configuration
# https://github.com/vxcozy/cc-stats

[general]
github_username = ""    # your GitHub username (for privacy filtering)
backfill = true         # fill activity grid for days with no local data

# Add one or more Claude Code accounts.
# Each account points to a Claude config directory.

[[accounts]]
path = "~/.claude"
```

## 3. Configure

Open `cc-stats.toml` and set your GitHub username:

```toml
[general]
github_username = "yourname"
```

The `github_username` field controls privacy filtering. When set, cc-stats calls `gh api` to list your public repos. Only project names matching a public repo are shown on the card. Everything else is redacted.

Leave the `accounts` section as-is unless you have multiple Claude installations (see [How-to: Add multiple accounts](howto.md#how-to-add-multiple-claude-accounts)).

## 4. Generate

```shell
cc-stats generate --out ./graph
```

Expected output:

```
Wrote ./graph/claude-stats.json
Wrote ./graph/claude-card.svg

1 account | 342 sessions | 89 active days | claude-sonnet-4-20250514
```

The numbers will differ based on your usage. If you see `0 sessions`, check that `~/.claude/projects/` exists and contains `.jsonl` files.

## 5. Inspect the output

`claude-stats.json` contains the raw data:

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
  "daily": { ... },
  "top_projects": [
    { "name": "myapp", "tokens": 5200000 },
    { "name": "dotfiles", "tokens": 1100000 }
  ]
}
```

`claude-card.svg` is a 480x380 SVG with a dark background, stat boxes, a contribution grid, and top project bars.

## 6. Embed in your GitHub profile

Copy the output files into your profile repo (the repo named after your GitHub username):

```shell
cp ./graph/claude-card.svg ~/Projects/yourname/
```

Add to your `README.md`:

```markdown
![Claude Code Stats](./claude-card.svg)
```

Commit and push. The card renders inline on your GitHub profile.

## 7. Keep it updated

Re-run `cc-stats generate` whenever you want to refresh the card. See [How-to: Automate updates](howto.md#how-to-automate-updates-with-a-local-script) for a cron-based approach.

## Next steps

- [How-to guides](howto.md) for specific tasks
- [Reference](reference.md) for every CLI flag and config option
- [Explanation](explanation.md) for how the data pipeline works
