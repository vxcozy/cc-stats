from pathlib import Path

from cc_stats.config import Config, load_config

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadConfig:
    def test_from_file(self):
        config = load_config(str(FIXTURES / "sample_config.toml"))
        assert config.github_username == "testuser"
        assert config.backfill is False
        assert len(config.account_paths) == 1

    def test_defaults_when_no_file(self, tmp_path):
        config = load_config(str(tmp_path / "nonexistent.toml"))
        assert config.github_username == ""
        assert config.backfill is True
        assert config.account_paths == [Path.home() / ".claude"]

    def test_missing_path_returns_defaults(self):
        # load_config with None searches standard paths, falls back to defaults
        config = load_config(None)
        assert isinstance(config, Config)
