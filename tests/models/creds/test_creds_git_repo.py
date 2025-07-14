import pytest
from pydantic import ValidationError

from models.creds.creds_git_repo import CredsGitRepo


def test_creds_git_repo_initialization_with_minimal_data():
    creds_git_repo = CredsGitRepo(name="test-repo")
    assert creds_git_repo.name == "test-repo"
    assert creds_git_repo.ssh_key_path is None
    assert creds_git_repo.username is None
    assert creds_git_repo.password is None


def test_creds_git_repo_initialization_with_all_fields():
    creds_git_repo = CredsGitRepo(
        name="test-repo",
        ssh_key_path="/path/to/ssh/key",
        username="test-user",
        password="test-password",
    )
    assert creds_git_repo.name == "test-repo"
    assert creds_git_repo.ssh_key_path == "/path/to/ssh/key"
    assert creds_git_repo.username == "test-user"
    assert creds_git_repo.password == "test-password"


def test_creds_git_repo_missing_mandatory_field_raises_error():
    with pytest.raises(ValidationError):
        CredsGitRepo(ssh_key_path="/path/to/ssh/key")
