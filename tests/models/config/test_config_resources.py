import pytest

from models.config.config_git_repo import ConfigGitRepo
from models.config.config_helm_chart import ConfigHelmChart
from models.config.config_image import ConfigImage
from models.config.config_resources import SyncResources


def test_sync_resources_initializes_empty_lists():
    sync = SyncResources([])
    assert len(sync.images) == 0
    assert len(sync.charts) == 0
    assert len(sync.repos) == 0


def test_sync_resources_adds_helm_chart():
    chart = ConfigHelmChart(
        type="helm",
        source_registry="source_registry",
        source_chart="source_chart",
        target_registry="target_registry",
        target_repo="target_repo",
        versions=["1.0.0"],
    )
    sync = SyncResources([chart])
    assert len(sync.charts) == 1
    assert sync.charts[0] == chart


def test_sync_resources_adds_image():
    image = ConfigImage(
        type="image", source="source_image", target="target_image", tags=["latest"]
    )
    sync = SyncResources([image])
    assert len(sync.images) == 1
    assert sync.images[0].source == image.source
    assert sync.images[0].target == image.target


def test_sync_resources_adds_git_repo():
    repo = ConfigGitRepo(
        type="git",
        source_repo="source_repo",
        target_repo="target_repo",
        push_mode="push",
        refs=["main"],
    )
    sync = SyncResources([repo])
    assert len(sync.repos) == 1
    assert sync.repos[0].source_repo == repo.source_repo
    assert sync.repos[0].target_repo == repo.target_repo


def test_sync_resources_raises_exception_for_invalid_resource():
    with pytest.raises(Exception, match="Unknown resource type:"):
        SyncResources(["invalid"])


def test_sync_resources_prevents_duplicate_helm_chart():
    chart = ConfigHelmChart(
        type="helm",
        source_registry="source_registry",
        source_chart="source_chart",
        target_registry="target_registry",
        target_repo="target_repo",
        versions=["1.0.0"],
    )
    sync = SyncResources([chart, chart])
    assert len(sync.charts) == 1


def test_sync_resources_prevents_duplicate_image():
    image = ConfigImage(
        type="image", source="source_image", target="target_image", tags=["latest"]
    )
    sync = SyncResources([image, image])
    assert len(sync.images) == 1


def test_sync_resources_prevents_duplicate_git_repo():
    repo = ConfigGitRepo(
        type="git",
        source_repo="source_repo",
        target_repo="target_repo",
        push_mode="push",
        refs=["main"],
    )
    sync = SyncResources([repo, repo])
    assert len(sync.repos) == 1
