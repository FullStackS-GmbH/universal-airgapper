from cnairgapper.models.config.config_git_repo import ConfigGitRepo
from cnairgapper.models.resources.git import GitRepo


def test_gitrepo_initialization():
    config_repo = ConfigGitRepo(
        type="github",
        source_repo="https://github.com/source/repo.git",
        target_repo="https://github.com/target/repo.git",
        push_mode="push",
        refs=["main", "develop"],
    )
    git_repo = GitRepo(config_repo)

    assert git_repo.type == "github"
    assert git_repo.source_repo == "https://github.com/source/repo.git"
    assert git_repo.target_repo == "https://github.com/target/repo.git"
    assert git_repo.push_mode == "push"
    assert git_repo.refs == ["main", "develop"]


def test_gitrepo_source_repo_host():
    config_repo = ConfigGitRepo(
        type="github",
        source_repo="https://github.com/source/repo.git",
        target_repo="https://github.com/target/repo.git",
        push_mode="push",
        refs=["main", "develop"],
    )
    git_repo = GitRepo(config_repo)

    assert git_repo.source_repo_host == "github.com"


def test_gitrepo_target_repo_host():
    config_repo = ConfigGitRepo(
        type="github",
        source_repo="https://github.com/source/repo.git",
        target_repo="https://gitlab.com/target/repo.git",
        push_mode="force",
        refs=["feature"],
    )
    git_repo = GitRepo(config_repo)

    assert git_repo.target_repo_host == "gitlab.com"


def test_gitrepo_invalid_url_parsing():
    config_repo = ConfigGitRepo(
        type="github",
        source_repo="invalid_url",
        target_repo="ftp://unsupported/repo.git",
        push_mode="skip",
        refs=["test"],
    )
    git_repo = GitRepo(config_repo)

    assert git_repo.source_repo_host == ""
    assert git_repo.target_repo_host == ""
