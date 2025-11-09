import pytest
from pydantic import ValidationError

from cnairgapper.models.config.config_helm_chart import ConfigHelmChart


def test_config_helm_chart_valid_data():
    data = {
        "type": "helm",
        "source_registry": "registry-source.example.com",
        "source_chart": "my-chart",
        "target_registry": "registry-target.example.com",
        "target_repo": "my-repo",
        "versions": ["1.0.0", "1.1.0"],
    }
    chart = ConfigHelmChart(**data)
    assert chart.type == "helm"
    assert chart.source_registry == "registry-source.example.com"
    assert chart.source_chart == "my-chart"
    assert chart.target_registry == "registry-target.example.com"
    assert chart.target_repo == "my-repo"
    assert chart.versions == ["1.0.0", "1.1.0"]
    assert chart.push_mode == "skip"


def test_config_helm_chart_missing_required_field():
    data = {
        "source_chart": "my-chart",
        "target_registry": "registry-target.example.com",
        "target_repo": "my-repo",
        "versions": ["1.0.0", "1.1.0"],
    }
    with pytest.raises(ValidationError):
        ConfigHelmChart(**data)


def test_config_helm_chart_invalid_version_type():
    data = {
        "type": "helm",
        "source_registry": "registry-source.example.com",
        "source_chart": "my-chart",
        "target_registry": "registry-target.example.com",
        "target_repo": "my-repo",
        "versions": "1.0.0",  # Should be a list, not a string
    }
    with pytest.raises(ValidationError):
        ConfigHelmChart(**data)


def test_config_helm_chart_push_mode_default():
    data = {
        "type": "helm",
        "source_registry": "registry-source.example.com",
        "source_chart": "my-chart",
        "target_registry": "registry-target.example.com",
        "target_repo": "my-repo",
        "versions": ["1.0.0"],
    }
    chart = ConfigHelmChart(**data)
    assert chart.push_mode == "skip"


def test_config_helm_chart_push_mode_custom_value():
    data = {
        "type": "helm",
        "source_registry": "registry-source.example.com",
        "source_chart": "my-chart",
        "target_registry": "registry-target.example.com",
        "target_repo": "my-repo",
        "versions": ["1.0.0"],
        "push_mode": "overwrite",
    }
    chart = ConfigHelmChart(**data)
    assert chart.push_mode == "overwrite"
