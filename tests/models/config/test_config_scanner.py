import pytest
from pydantic import ValidationError

from cnairgapper.models.config.config_scanner import ConfigScanner


def test_config_scanner_valid_instance():
    config = ConfigScanner(
        name="example_scanner",
        type="neuvector",
        threshold_critical=10,
        threshold_high=20,
        threshold_medium=30,
        threshold_low=40,
    )
    assert config.name == "example_scanner"
    assert config.type == "neuvector"
    assert config.threshold_critical == 10
    assert config.threshold_high == 20
    assert config.threshold_medium == 30
    assert config.threshold_low == 40


def test_config_scanner_missing_name():
    with pytest.raises(ValidationError):
        ConfigScanner(
            type="snyk",
            threshold_critical=10,
            threshold_high=20,
            threshold_medium=30,
            threshold_low=40,
        )


def test_config_scanner_invalid_type():
    with pytest.raises(ValidationError):
        ConfigScanner(
            name="example_scanner",
            type="invalid_type",
            threshold_critical=10,
            threshold_high=20,
            threshold_medium=30,
            threshold_low=40,
        )


def test_config_scanner_defaults():
    config = ConfigScanner(name="default_scanner", type="cnspec")
    assert config.threshold_critical == 0
    assert config.threshold_high == 0
    assert config.threshold_medium == 0
    assert config.threshold_low == 0
