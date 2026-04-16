"""Session data types shared across parsers."""

from dataclasses import dataclass, field


@dataclass
class SessionData:
    """Normalized session metrics from any data source."""

    cli_session_id: str
    source: str  # "jsonl" | "desktop_meta"
    user_msgs: int = 0
    assistant_msgs: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_min: float = 0.0
    day: str = ""  # YYYY-MM-DD
    models: dict[str, int] = field(default_factory=dict)
    hours: dict[int, int] = field(default_factory=dict)
    project: str = "misc"
