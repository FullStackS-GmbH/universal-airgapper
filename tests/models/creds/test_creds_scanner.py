import pytest
from pydantic import ValidationError

from cnairgapper.models.creds.creds_scanner import CredsScanner


def test_creds_scanner_initialization():
    scanner = CredsScanner(
        name="TestScanner", type="test-type", username="test-user", password="test-pass"
    )
    assert scanner.name == "TestScanner"
    assert scanner.type == "test-type"
    assert scanner.username == "test-user"
    assert scanner.password == "test-pass"


def test_creds_scanner_with_empty_fields():
    with pytest.raises(ValidationError):  # Ensures Pydantic enforces field validation
        CredsScanner(name="", type="", username="", password="")
