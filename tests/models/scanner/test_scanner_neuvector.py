import pytest

from models.config.config_image import ConfigImage
from models.config.config_scanner_neuvector import ConfigNeuvectorScanner
from models.creds.creds_scanner import CredsScanner
from models.resources.image import Image
from models.scanner.scanner_neuvector import ScannerNeuVector


@pytest.fixture
def sample_credentials():
    return CredsScanner(
        name="test_scanner",
        type="neuvector",
        username="test_user",
        password="test_password",
    )


@pytest.fixture
def sample_config():
    return ConfigNeuvectorScanner(
        name="neuvector_scanner",
        hostname="neuvector.example.com",
        type="neuvector",
        port=443,
        verify_tls=True,
    )


@pytest.fixture
def sample_image():
    return Image(
        config_image=ConfigImage(
            type="image",
            source="test_registry/test_repo:test_tag",
            target="target_registry/target_repo:target_tag",
            scan="neuvector",
            tags=["latest", "stable"],
        )
    )


@pytest.fixture
def scanner(sample_credentials, sample_config):
    return ScannerNeuVector(credentials=sample_credentials, config=sample_config)


def test_validate_connection(scanner, requests_mock):
    requests_mock.delete(
        "https://neuvector.example.com:443", json={"code": 1, "error": "URL not found"}
    )
    assert scanner.validate_connection() is True


def test_fetch_nv_token(scanner, requests_mock):
    requests_mock.post(
        "https://neuvector.example.com:443/v1/auth",
        json={"token": {"token": "test_token"}},
    )
    assert scanner.fetch_nv_token() is True
    assert scanner.token == "test_token"


def test_invalidate_nv_token(scanner, requests_mock):
    scanner.token = "test_token"
    requests_mock.delete("https://neuvector.example.com:443/v1/auth", status_code=200)
    assert scanner.invalidate_nv_token() is True


def test_process_result(scanner):
    report = {
        "vulnerabilities": [
            {"severity": "Critical"},
            {"severity": "High"},
            {"severity": "Medium"},
            {"severity": "Low"},
            {"severity": "Low"},
            {"severity": "Low"},
            {"severity": "Info"},
        ]
    }
    scanner.config.threshold_low = 1
    scanner.config.threshold_medium = 1
    scanner.config.threshold_high = 1
    scanner.config.threshold_critical = 1

    result = scanner.neuvector_2_scanner_result(report)
    assert result.issues_critical == 1
    assert result.issues_high == 1
    assert result.issues_medium == 1
    assert result.issues_low == 3
    assert result.issues_unknown == 1
    assert result.ok is False
    assert result.msg.startswith("low threshold exceeded")


def test_scan_image(scanner, sample_image, requests_mock):
    requests_mock.post(
        "https://neuvector.example.com:443/v1/auth",
        json={"token": {"token": "test_token"}},
    )
    requests_mock.post(
        "https://neuvector.example.com:443/v1/scan/repository",
        json={"report": {"vulnerabilities": []}},
    )
    requests_mock.delete("https://neuvector.example.com:443/v1/auth", status_code=200)

    result = scanner.scan_image(
        image=sample_image,
        tag="latest",
        registry_username="registry_user",
        registry_password="registry_pass",
    )
    assert result.ok is True
    assert result.msg == "result fine"
