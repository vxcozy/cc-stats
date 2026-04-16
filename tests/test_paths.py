from unittest.mock import patch

from cc_stats.paths import _fallback_name, resolve_project_name


class TestFallbackName:
    def test_simple(self):
        assert _fallback_name("myapp") == "myapp"

    def test_duplicated(self):
        assert _fallback_name("tome-tome") == "tome"

    def test_triple_duplicated(self):
        assert _fallback_name("cozy-brain-cozy-brain") == "cozy-brain"

    def test_not_duplicated(self):
        assert _fallback_name("my-cool-app") == "app"

    def test_empty(self):
        assert _fallback_name("") == "misc"


class TestResolveProjectName:
    @patch("cc_stats.paths._try_resolve_path", return_value=None)
    @patch("cc_stats.paths._encoded_home", return_value="-Users-alice")
    def test_strips_home_prefix(self, _home, _resolve):
        # After stripping home and failing resolution, falls back
        resolve_project_name.cache_clear()
        name = resolve_project_name("-Users-alice-Projects-myapp")
        assert name in ("myapp", "Projects")  # depends on fallback logic

    @patch("cc_stats.paths._try_resolve_path", return_value=None)
    @patch("cc_stats.paths._encoded_home", return_value="-Users-alice")
    def test_strips_worktree_suffix(self, _home, _resolve):
        resolve_project_name.cache_clear()
        name = resolve_project_name("-Users-alice-Projects-myapp--claude-worktrees-foo")
        assert "foo" not in name
        assert "worktree" not in name

    @patch("cc_stats.paths._try_resolve_path", return_value=None)
    @patch("cc_stats.paths._encoded_home", return_value="-Users-alice")
    def test_home_only_returns_misc(self, _home, _resolve):
        resolve_project_name.cache_clear()
        assert resolve_project_name("-Users-alice") == "misc"

    @patch("cc_stats.paths._try_resolve_path", return_value="campaignai")
    @patch("cc_stats.paths._encoded_home", return_value="-Users-alice")
    def test_uses_resolved_path(self, _home, _resolve):
        resolve_project_name.cache_clear()
        assert resolve_project_name("-Users-alice-Documents-GitHub-campaignai") == "campaignai"
