from cnairgapper.models.config.config_file import ConfigFile
from cnairgapper.models.config.config_git_repo import ConfigGitRepo
from cnairgapper.models.config.config_helm_chart import ConfigHelmChart
from cnairgapper.models.config.config_image import ConfigImage
from cnairgapper.models.config.config_scanner_neuvector import ConfigNeuvectorScanner


def test_config_file_empty_resources_and_scanners_default():
    config = ConfigFile()
    assert config.resources == []
    assert config.scanners == []


def test_config_file_with_populated_resources():
    resource = ConfigGitRepo(
        type="git",
        source_repo="https://example.com/source.git",
        target_repo="https://example.com/target.git",
        push_mode="push",
        refs=["main", "develop"],
    )
    config = ConfigFile(resources=[resource])
    assert len(config.resources) == 1
    assert isinstance(config.resources[0], ConfigGitRepo)
    assert config.resources[0].source_repo == "https://example.com/source.git"


def test_config_file_with_populated_scanners():
    scanner = ConfigNeuvectorScanner(
        hostname="scanner.example.com",
        port=443,
        verify_tls=True,
        type="neuvector",
        name="neuvector-scanner",
    )
    config = ConfigFile(scanners=[scanner])
    assert len(config.scanners) == 1
    assert isinstance(config.scanners[0], ConfigNeuvectorScanner)
    assert config.scanners[0].hostname == "scanner.example.com"


def test_config_file_with_mixed_resources():
    git_resource = ConfigGitRepo(
        type="git",
        source_repo="https://example.com/source.git",
        target_repo="https://example.com/target.git",
        push_mode="force",
        refs=["main"],
    )
    image_resource = ConfigImage(
        type="image",
        source="image-source",
        target="image-target",
        scan="full",
        tags=["v1.0", "v1.1"],
    )
    helm_chart_resource = ConfigHelmChart(
        type="helm-chart",
        source_registry="source-registry",
        source_chart="source-chart",
        target_registry="target-registry",
        target_repo="target-repo",
        versions=["1.0.0", "2.0.0"],
        push_mode="skip",
    )
    config = ConfigFile(resources=[git_resource, image_resource, helm_chart_resource])
    assert len(config.resources) == 3
    assert isinstance(config.resources[0], ConfigGitRepo)
    assert isinstance(config.resources[1], ConfigImage)
    assert isinstance(config.resources[2], ConfigHelmChart)
