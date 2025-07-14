from models.config.config_helm_chart import ConfigHelmChart
from models.resources.helm import HelmChart


def test_helm_chart_initialization():
    config_chart = ConfigHelmChart(
        type="chart",
        source_registry="source-registry",
        source_chart="source-chart",
        target_registry="target-registry",
        target_repo="target-repo",
        versions=["1.0.0"],
        push_mode="skip",
    )
    version = "1.0.0"
    helm_chart = HelmChart(config_chart=config_chart, version=version)

    assert helm_chart.source == "source-chart"
    assert helm_chart.source_registry == "source-registry"
    assert helm_chart.target_repo == "target-repo"
    assert helm_chart.target_registry == "target-registry"
    assert helm_chart.version == "1.0.0"
    assert helm_chart.push_mode == "skip"


def test_helm_chart_chart_name_with_slash_in_source():
    config_chart = ConfigHelmChart(
        type="chart",
        source_registry="source-registry",
        source_chart="myrepo/source-chart",
        target_registry="target-registry",
        target_repo="target-repo",
        versions=["1.0.0"],
        push_mode="skip",
    )
    version = "1.0.0"
    helm_chart = HelmChart(config_chart=config_chart, version=version)

    assert helm_chart.chart_name == "source-chart"


def test_helm_chart_chart_name_without_slash_in_source():
    config_chart = ConfigHelmChart(
        type="chart",
        source_registry="source-registry",
        source_chart="source-chart",
        target_registry="target-registry",
        target_repo="target-repo",
        versions=["1.0.0"],
        push_mode="skip",
    )
    version = "1.0.0"
    helm_chart = HelmChart(config_chart=config_chart, version=version)

    assert helm_chart.chart_name == "source-chart"
