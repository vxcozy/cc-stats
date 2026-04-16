# cc-stats

Aggregate Claude Code session data from local files and generate an SVG card for your GitHub profile.

Reads JSONL session logs and desktop app metadata, merges and deduplicates them, computes streaks/tokens/projects, and outputs a `claude-card.svg` with a contribution grid and stats.

## Install

```shell
pip install cc-stats
```

Requires Python 3.11+. No runtime dependencies.

## Quick start

```shell
cc-stats init
```

This creates `cc-stats.toml` in the current directory. Open it and set your GitHub username:

```toml
[general]
github_username = "yourname"
```

Generate the card:

```shell
cc-stats generate --out ./graph
```

Two files appear in `./graph/`:

- `claude-stats.json` -- aggregated session data
- `claude-card.svg` -- the SVG card

Embed it in your GitHub profile README:

```markdown
![Claude Code Stats](./graph/claude-card.svg)
```

## Config

See [docs/reference.md](docs/reference.md) for the full config spec.

The default config points at `~/.claude`. If you use multiple Claude accounts or a non-default path, add `[[accounts]]` entries:

```toml
[[accounts]]
path = "~/.claude"

[[accounts]]
path = "/home/me/.claude-work"
```

## Privacy

Project names in the SVG are redacted unless they match a public repo on your GitHub account. If `github_username` is empty or `gh` is not installed, all project names show as `[redacted]`.

## Documentation

- [Tutorial](docs/tutorial.md) -- step-by-step setup
- [How-to guides](docs/howto.md) -- specific tasks
- [Reference](docs/reference.md) -- CLI, config, output formats
- [Explanation](docs/explanation.md) -- how things work under the hood

## License

MIT
