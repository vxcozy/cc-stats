import xml.etree.ElementTree as ET
from unittest.mock import patch

from cc_stats.aggregator import DailyBucket, Stats
from cc_stats.svg.card import render_card
from cc_stats.svg.constants import CARD_HEIGHT, CARD_WIDTH


def _sample_stats() -> Stats:
    return Stats(
        generated="2026-04-16T00:00:00Z",
        accounts=2,
        total_sessions=100,
        total_messages=36000,
        total_tokens=4_100_000_000,
        active_days=23,
        current_streak=11,
        longest_streak=11,
        peak_hour=15,
        favorite_model="claude-opus-4-6",
        daily={
            "2026-04-15": DailyBucket(sessions=5, user_msgs=100, assistant_msgs=150),
            "2026-04-16": DailyBucket(sessions=3, user_msgs=50, assistant_msgs=80),
        },
        top_projects=[
            ("myapp", 2_700_000_000),
            ("clitunes", 1_100_000_000),
        ],
    )


class TestRenderCard:
    def test_valid_xml(self):
        svg = render_card(_sample_stats(), {"clitunes"})
        # Should parse without error
        ET.fromstring(svg)

    def test_dimensions(self):
        svg = render_card(_sample_stats(), set())
        root = ET.fromstring(svg)
        assert root.attrib["width"] == str(CARD_WIDTH)
        assert root.attrib["height"] == str(CARD_HEIGHT)

    def test_contains_stats(self):
        svg = render_card(_sample_stats(), set())
        assert "100" in svg  # sessions
        assert "36.0k" in svg  # messages
        assert "4.1B" in svg  # tokens
        assert "23" in svg  # active days
        assert "opus-4-6" in svg  # model

    def test_privacy_redaction(self):
        svg = render_card(_sample_stats(), {"clitunes"})
        assert "clitunes" in svg
        assert "[redacted]" in svg  # myapp is not in public repos

    def test_all_redacted_when_no_public_repos(self):
        svg = render_card(_sample_stats(), set())
        assert svg.count("[redacted]") == 2

    def test_subtitle_accounts(self):
        stats = _sample_stats()
        stats.accounts = 2
        svg = render_card(stats, set())
        assert "2 accounts" in svg

    def test_subtitle_single_account(self):
        stats = _sample_stats()
        stats.accounts = 1
        svg = render_card(stats, set())
        assert "1 account" in svg
        assert "1 accounts" not in svg
