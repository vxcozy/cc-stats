"""Privacy filtering: resolve which projects are public via gh CLI."""

import subprocess


def get_public_repos(github_username: str) -> set[str]:
    """Fetch public repo names for a GitHub user via the gh CLI.

    Returns an empty set if gh is not installed, not authenticated,
    times out, or the username is empty. When the set is empty,
    all projects should be treated as private (redacted).
    """
    if not github_username:
        return set()

    try:
        result = subprocess.run(
            [
                "gh", "api",
                f"users/{github_username}/repos",
                "--jq", ".[].name",
                "--paginate",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return set(result.stdout.strip().split("\n"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return set()


def redact_project_name(name: str, public_repos: set[str]) -> str:
    """Return the project name if it matches a public repo, otherwise '[redacted]'."""
    if not public_repos:
        return "[redacted]"
    if name.lower() in {r.lower() for r in public_repos}:
        return name
    return "[redacted]"
