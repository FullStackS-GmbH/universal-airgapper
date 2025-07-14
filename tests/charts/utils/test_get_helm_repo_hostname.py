from charts.utils import get_helm_repo_hostname


def test_get_helm_repo_hostname_with_https_url():
    """
    Test get_helm_repo_hostname with an HTTPS URL.
    """
    repo_url = "https://charts.helm.sh/stable"
    expected_hostname = "charts.helm.sh"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_with_http_url():
    """
    Test get_helm_repo_hostname with an HTTP URL.
    """
    repo_url = "http://localhost:8080/charts"
    expected_hostname = "localhost"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_without_protocol():
    """
    Test get_helm_repo_hostname with a URL without protocol.
    """
    repo_url = "localhost:8080/charts"
    expected_hostname = "localhost"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_without_path():
    """
    Test get_helm_repo_hostname with a URL without path elements.
    """
    repo_url = "https://charts.helm.sh"
    expected_hostname = "charts.helm.sh"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_with_port_only():
    """
    Test get_helm_repo_hostname with a URL that only includes a port.
    """
    repo_url = "http://localhost:8080"
    expected_hostname = "localhost"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_with_trailing_slash():
    """
    Test get_helm_repo_hostname with a URL that ends with a trailing slash.
    """
    repo_url = "https://charts.helm.sh/"
    expected_hostname = "charts.helm.sh"
    assert get_helm_repo_hostname(repo_url) == expected_hostname


def test_get_helm_repo_hostname_empty_url():
    """
    Test get_helm_repo_hostname with an empty string.
    """
    repo_url = ""
    expected_hostname = ""
    assert get_helm_repo_hostname(repo_url) == expected_hostname
