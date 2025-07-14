import pytest
from pydantic import ValidationError

from models.creds.creds_helm_registry import CredsHelmRegistry


def test_creds_helm_registry_initialization():
    registry = CredsHelmRegistry(
        name="TestRegistry", username="test_user", password="test_password"
    )
    assert registry.name == "TestRegistry"
    assert registry.username == "test_user"
    assert registry.password == "test_password"


def test_creds_helm_registry_with_empty_fields():
    with pytest.raises(ValidationError):
        CredsHelmRegistry(name="", username="test_user", password="test_password")
