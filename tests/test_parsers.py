from pathlib import Path

from cc_stats.parsers.desktop import parse_session as parse_desktop_session
from cc_stats.parsers.jsonl import parse_session as parse_jsonl_session

FIXTURES = Path(__file__).parent / "fixtures"


class TestJsonlParser:
    def test_valid_session(self):
        session = parse_jsonl_session(FIXTURES / "sample_session.jsonl")
        assert session is not None
        assert session.user_msgs == 2
        assert session.assistant_msgs == 2
        assert session.input_tokens == 100 + 500 + 200 + 150 + 0 + 600  # 1550
        assert session.output_tokens == 50 + 80  # 130
        assert session.day == "2026-03-15"
        assert "claude-opus-4-6" in session.models
        assert session.models["claude-opus-4-6"] == 2
        assert session.source == "jsonl"

    def test_nonexistent_file(self):
        session = parse_jsonl_session(Path("/nonexistent/file.jsonl"))
        assert session is None

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.jsonl"
        empty.write_text("")
        session = parse_jsonl_session(empty)
        assert session is None

    def test_malformed_json_skipped(self, tmp_path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text(
            'not json\n'
            '{"type":"user","message":{},"timestamp":"2026-01-01T00:00:00Z","sessionId":"x"}\n'
            '{corrupted\n'
        )
        session = parse_jsonl_session(bad)
        assert session is not None
        assert session.user_msgs == 1


class TestDesktopParser:
    def test_valid_metadata(self):
        session = parse_desktop_session(FIXTURES / "sample_desktop_meta.json")
        assert session is not None
        assert session.cli_session_id == "desktop-session-001"
        assert session.user_msgs == 25  # completedTurns
        assert session.assistant_msgs == 25
        assert session.source == "desktop_meta"
        assert session.project == "myapp"
        assert "claude-sonnet-4-6" in session.models

    def test_missing_file(self):
        session = parse_desktop_session(Path("/nonexistent.json"))
        assert session is None

    def test_missing_required_fields(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text('{"sessionId": "x"}')
        session = parse_desktop_session(bad)
        assert session is None
