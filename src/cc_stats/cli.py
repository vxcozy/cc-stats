"""CLI entry point: cc-stats generate | cc-stats init."""

import argparse
import json
import os
import sys

from cc_stats import __version__
from cc_stats.aggregator import aggregate, get_first_token_date
from cc_stats.config import generate_template, load_config
from cc_stats.parsers.desktop import count_accounts, parse_all as parse_desktop
from cc_stats.parsers.jsonl import parse_all as parse_jsonl
from cc_stats.privacy import get_public_repos
from cc_stats.svg.card import render_card


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cc-stats",
        description="Aggregate Claude Code session data and generate a GitHub profile SVG card.",
    )
    parser.add_argument("--version", action="version", version=f"cc-stats {__version__}")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate stats JSON and SVG card")
    gen.add_argument("--config", help="Path to cc-stats.toml (default: auto-detect)")
    gen.add_argument("--out", default=".", help="Output directory (default: current dir)")

    init = sub.add_parser("init", help="Create a cc-stats.toml template")
    init.add_argument("--dest", default=".", help="Directory to write cc-stats.toml")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.config, args.out)
    elif args.command == "init":
        cmd_init(args.dest)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_init(dest: str) -> None:
    path = os.path.join(dest, "cc-stats.toml")
    if os.path.exists(path):
        print(f"cc-stats.toml already exists at {path}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(dest, exist_ok=True)
    with open(path, "w") as f:
        f.write(generate_template())
    print(f"Created {path}")


def cmd_generate(config_path: str | None, out_dir: str) -> None:
    config = load_config(config_path)
    os.makedirs(out_dir, exist_ok=True)

    # Parse sessions from both sources
    jsonl_sessions = parse_jsonl(config.account_paths)
    desktop_sessions = parse_desktop()
    accounts = count_accounts()
    first_token = get_first_token_date(config.account_paths)

    # Aggregate
    stats = aggregate(
        jsonl_sessions=jsonl_sessions,
        desktop_sessions=desktop_sessions,
        accounts=max(accounts, len(config.account_paths)),
        backfill=config.backfill,
        first_token_date=first_token,
    )

    # Privacy filter
    public_repos = get_public_repos(config.github_username)

    # Write JSON
    json_path = os.path.join(out_dir, "claude-stats.json")
    with open(json_path, "w") as f:
        json.dump(stats.to_dict(), f, indent=2)

    # Write SVG
    svg_path = os.path.join(out_dir, "claude-card.svg")
    with open(svg_path, "w") as f:
        f.write(render_card(stats, public_repos))

    s = stats
    print(f"Wrote {json_path}")
    print(f"Wrote {svg_path}")
    print(
        f"\n{s.accounts} account{'s' if s.accounts > 1 else ''} | "
        f"{s.total_sessions} sessions | {s.active_days} active days | "
        f"{s.favorite_model}"
    )
