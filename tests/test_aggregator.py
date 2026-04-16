from datetime import datetime
from unittest.mock import patch

from cc_stats.aggregator import DailyBucket, aggregate, compute_streaks
from cc_stats.parsers import SessionData


def _session(cli_id: str, day: str, source: str = "jsonl", **kwargs) -> SessionData:
    return SessionData(
        cli_session_id=cli_id,
        source=source,
        user_msgs=kwargs.get("user_msgs", 5),
        assistant_msgs=kwargs.get("assistant_msgs", 5),
        input_tokens=kwargs.get("input_tokens", 1000),
        output_tokens=kwargs.get("output_tokens", 500),
        duration_min=kwargs.get("duration_min", 30.0),
        day=day,
        models=kwargs.get("models", {"claude-opus-4-6": 5}),
        hours=kwargs.get("hours", {10: 5}),
        project=kwargs.get("project", "myapp"),
    )


class TestComputeStreaks:
    def test_empty(self):
        assert compute_streaks([]) == (0, 0)

    @patch("cc_stats.aggregator.datetime")
    def test_single_day_today(self, mock_dt):
        today = "2026-04-16"
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime
        assert compute_streaks([today]) == (1, 1)

    @patch("cc_stats.aggregator.datetime")
    def test_single_day_old(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime
        assert compute_streaks(["2026-04-10"]) == (0, 1)

    @patch("cc_stats.aggregator.datetime")
    def test_consecutive_streak(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime
        days = ["2026-04-12", "2026-04-13", "2026-04-14", "2026-04-15", "2026-04-16"]
        assert compute_streaks(days) == (5, 5)

    @patch("cc_stats.aggregator.datetime")
    def test_gap_splits_streaks(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime
        days = ["2026-04-10", "2026-04-11", "2026-04-12", "2026-04-15", "2026-04-16"]
        current, longest = compute_streaks(days)
        assert current == 2
        assert longest == 3


class TestAggregate:
    @patch("cc_stats.aggregator.datetime")
    def test_deduplication_jsonl_wins(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime

        jsonl = [_session("s1", "2026-04-16", source="jsonl", user_msgs=10)]
        desktop = [_session("s1", "2026-04-16", source="desktop_meta", user_msgs=2)]

        stats = aggregate(jsonl, desktop, backfill=False)
        # JSONL's 10 user_msgs should win over desktop's 2
        bucket = stats.daily["2026-04-16"]
        assert bucket.user_msgs == 10

    @patch("cc_stats.aggregator.datetime")
    def test_backfill_creates_entries(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 5)
        mock_dt.strptime = datetime.strptime

        sessions = [_session("s1", "2026-04-05")]
        stats = aggregate(sessions, [], backfill=True, first_token_date="2026-04-01")

        # Should have Apr 1-5 (5 days)
        assert stats.active_days == 5
        # Backfilled days should not count toward total_sessions
        assert stats.total_sessions == 1

    @patch("cc_stats.aggregator.datetime")
    def test_no_backfill_when_disabled(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 5)
        mock_dt.strptime = datetime.strptime

        sessions = [_session("s1", "2026-04-05")]
        stats = aggregate(sessions, [], backfill=False, first_token_date="2026-04-01")
        assert stats.active_days == 1

    @patch("cc_stats.aggregator.datetime")
    def test_top_projects(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 4, 16)
        mock_dt.strptime = datetime.strptime

        sessions = [
            _session("s1", "2026-04-16", project="big", input_tokens=5000, output_tokens=3000),
            _session("s2", "2026-04-16", project="small", input_tokens=100, output_tokens=50),
        ]
        stats = aggregate(sessions, [], backfill=False)
        assert stats.top_projects[0][0] == "big"
        assert stats.top_projects[0][1] == 8000
