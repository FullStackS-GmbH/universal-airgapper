import requests

from charts.utils import is_oci_registry


def test_is_oci_registry_v2_api_200(requests_mock):
    """
    Test if the function correctly identifies an OCI registry when
    the repository v2 API endpoint responds with a 200 status code.
    """
    repo_url = "https://example.com/registry"
    headers = {"Authorization": "Bearer token123"}

    v2_url = "https://example.com/registry/v2/"
    requests_mock.get(v2_url, status_code=200)

    assert is_oci_registry(repo_url, headers) is True


def test_is_oci_registry_v2_api_401(requests_mock):
    """
    Test if the function correctly identifies an OCI registry when
    the repository v2 API endpoint responds with a 401 status code.
    """
    repo_url = "https://example.com/registry"
    headers = {"Authorization": "Bearer token123"}

    v2_url = "https://example.com/registry/v2/"
    requests_mock.get(v2_url, status_code=401)

    assert is_oci_registry(repo_url, headers) is True


def test_is_oci_registry_v2_api_404(requests_mock):
    """
    Test if the function correctly identifies a non-OCI registry when
    the repository v2 API endpoint responds with a 404 status code.
    """
    repo_url = "https://example.com/registry"
    headers = {"Authorization": "Bearer token123"}

    v2_url = "https://example.com/registry/v2/"
    requests_mock.get(v2_url, status_code=404)

    legacy_url = "https://example.com/registry/index.yaml"
    requests_mock.head(legacy_url, status_code=404)

    assert is_oci_registry(repo_url, headers) is False


def test_is_oci_registry_request_exception(requests_mock):
    """
    Test if the function correctly identifies a non-OCI registry when
    an exception occurs during the requests.
    """
    repo_url = "https://example.com/registry"
    headers = {"Authorization": "Bearer token123"}

    v2_url = "https://example.com/registry/v2/"
    legacy_url = "https://example.com/registry/index.yaml"
    requests_mock.get(v2_url, exc=requests.exceptions.RequestException)
    requests_mock.head(legacy_url, exc=requests.exceptions.RequestException)

    assert is_oci_registry(repo_url, headers) is False
