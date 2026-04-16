from cc_stats.formatters import fmt_hour, fmt_num


class TestFmtNum:
    def test_zero(self):
        assert fmt_num(0) == "0"

    def test_small(self):
        assert fmt_num(42) == "42"

    def test_boundary_below_k(self):
        assert fmt_num(999) == "999"

    def test_thousands(self):
        assert fmt_num(1_000) == "1.0k"
        assert fmt_num(1_500) == "1.5k"
        assert fmt_num(33_900) == "33.9k"

    def test_millions(self):
        assert fmt_num(1_000_000) == "1.0M"
        assert fmt_num(1_500_000) == "1.5M"
        assert fmt_num(125_600_000) == "125.6M"

    def test_billions(self):
        assert fmt_num(1_000_000_000) == "1.0B"
        assert fmt_num(4_100_000_000) == "4.1B"


class TestFmtHour:
    def test_midnight(self):
        assert fmt_hour(0) == "12 AM"

    def test_morning(self):
        assert fmt_hour(1) == "1 AM"
        assert fmt_hour(11) == "11 AM"

    def test_noon(self):
        assert fmt_hour(12) == "12 PM"

    def test_afternoon(self):
        assert fmt_hour(13) == "1 PM"
        assert fmt_hour(23) == "11 PM"
