import pytest
from pydantic import ValidationError

from models.config.config_git_repo import ConfigGitRepo


def test_config_git_repo_valid_data():
    config = ConfigGitRepo(
        type="git",
        source_repo="https://github.com/source_repo",
        target_repo="https://github.com/target_repo",
        push_mode="push",
        refs=["main", "develop"],
    )
    assert config.type == "git"
    assert config.source_repo == "https://github.com/source_repo"
    assert config.target_repo == "https://github.com/target_repo"
    assert config.push_mode == "push"
    assert config.refs == ["main", "develop"]


def test_config_git_repo_invalid_push_mode():
    with pytest.raises(ValidationError):
        ConfigGitRepo(
            type="git",
            source_repo="https://github.com/source_repo",
            target_repo="https://github.com/target_repo",
            push_mode="invalid_mode",
            refs=["main", "develop"],
        )


def test_config_git_repo_empty_refs():
    config = ConfigGitRepo(
        type="git",
        source_repo="https://github.com/source_repo",
        target_repo="https://github.com/target_repo",
        push_mode="skip",
        refs=[],
    )
    assert config.refs == []


def test_config_git_repo_missing_required_field():
    with pytest.raises(ValidationError):
        ConfigGitRepo(
            target_repo="https://github.com/target_repo",
            push_mode="skip",
            refs=["main"],
        )
