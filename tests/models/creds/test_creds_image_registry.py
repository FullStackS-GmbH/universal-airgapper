import pytest
from pydantic import ValidationError

from models.creds.creds_image_registry import CredsImageRegistry


def test_creds_image_registry_initialization():
    registry = CredsImageRegistry(
        name="test_registry", username="user123", password="pass123"
    )
    assert registry.name == "test_registry"
    assert registry.username == "user123"
    assert registry.password == "pass123"


def test_creds_image_registry_invalid_name():
    with pytest.raises(ValidationError):
        CredsImageRegistry(name="", username="user123", password="pass123")
