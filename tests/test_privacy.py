from unittest.mock import patch

from cc_stats.privacy import get_public_repos, redact_project_name


class TestRedactProjectName:
    def test_public_repo_shown(self):
        assert redact_project_name("myapp", {"myapp", "other"}) == "myapp"

    def test_case_insensitive(self):
        assert redact_project_name("MyApp", {"myapp"}) == "MyApp"

    def test_private_repo_redacted(self):
        assert redact_project_name("secret", {"myapp"}) == "[redacted]"

    def test_empty_repos_all_redacted(self):
        assert redact_project_name("anything", set()) == "[redacted]"


class TestGetPublicRepos:
    @patch("cc_stats.privacy.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "repo1\nrepo2\nrepo3\n"
        result = get_public_repos("testuser")
        assert result == {"repo1", "repo2", "repo3"}

    @patch("cc_stats.privacy.subprocess.run")
    def test_failure(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        result = get_public_repos("testuser")
        assert result == set()

    @patch("cc_stats.privacy.subprocess.run", side_effect=FileNotFoundError)
    def test_gh_not_installed(self, mock_run):
        result = get_public_repos("testuser")
        assert result == set()

    def test_empty_username(self):
        assert get_public_repos("") == set()
