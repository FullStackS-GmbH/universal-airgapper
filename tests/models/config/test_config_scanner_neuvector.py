import pytest
from pydantic import ValidationError

from cnairgapper.models.config.config_scanner_neuvector import ConfigNeuvectorScanner


def test_config_neuvector_scanner_init():
    scanner = ConfigNeuvectorScanner(
        name="MyScanner",
        type="neuvector",
        hostname="localhost",
        port=8080,
        verify_tls=True,
        threshold_critical=10,
        threshold_high=20,
        threshold_medium=30,
        threshold_low=40,
    )
    assert scanner.name == "MyScanner"
    assert scanner.type == "neuvector"
    assert scanner.hostname == "localhost"
    assert scanner.port == 8080
    assert scanner.verify_tls is True
    assert scanner.threshold_critical == 10
    assert scanner.threshold_high == 20
    assert scanner.threshold_medium == 30
    assert scanner.threshold_low == 40


def test_config_neuvector_scanner_missing_fields():
    with pytest.raises(ValidationError):
        ConfigNeuvectorScanner(name="IncompleteScanner", type="neuvector")


def test_config_neuvector_scanner_invalid_type():
    with pytest.raises(ValidationError):
        ConfigNeuvectorScanner(
            name="InvalidScanner",
            type="invalid_type",
            hostname="localhost",
            port=8080,
            verify_tls=False,
        )
