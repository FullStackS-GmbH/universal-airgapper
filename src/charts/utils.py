import logging
import os
import tarfile
import tempfile
from http import HTTPStatus

import requests
import yaml

from cli.utils import get_registry_token
from models.creds.creds import Creds
from models.rc import RC
from models.resources.helm import HelmChart


def extract_chart_info(chart_path: str) -> dict[str, str]:
    """Extract Helm chart information from a tar.gz file.

    This function takes the file path of a Helm chart archive in tar.gz format, reads
    the Chart.yaml file inside it, and extracts the name and version of the chart. If
    the Chart.yaml file is not found in the archive, an exception is raised.

    Args:
        chart_path (str): The file path of the tar.gz Helm chart archive.

    Returns:
        Dict[str, str]: A dictionary containing the name and version of the chart
        extracted from the Chart.yaml file.

    Raises:
        ValueError: If the Chart.yaml file cannot be found within the given archive.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(chart_path, "r:gz") as tar:
            # Find and extract Chart.yaml
            for member in tar.getmembers():
                if member.name.endswith("Chart.yaml"):
                    tar.extract(member, temp_dir)
                    chart_yaml_path = os.path.join(temp_dir, member.name)
                    with open(chart_yaml_path, encoding="utf-8") as f:
                        chart_yaml = yaml.safe_load(f)
                    return {
                        "name": chart_yaml["name"],
                        "version": chart_yaml["version"],
                    }
    raise ValueError("Could not find Chart.yaml in the archive")


def get_helm_repo_hostname(repo_url: str) -> str:
    """Extracts and returns the hostname from a given Helm repository URL.

    This function takes a Helm repository URL as input and processes it to
    return only the hostname by removing the protocol, any paths, and the port
    (if present).

    Args:
        repo_url (str): The Helm repository URL to extract the hostname from.

    Returns:
        str: The extracted hostname.
    """
    # Remove protocol if present
    if "://" in repo_url:
        hostname = repo_url.split("://")[1]
    else:
        hostname = repo_url

    # Remove path if present
    hostname = hostname.split("/")[0]

    # Remove port if present
    hostname = hostname.split(":")[0]

    return hostname


def is_oci_registry(repo_url: str, headers: dict) -> bool:
    """Determine if a given repository URL corresponds to an OCI registry.

    This function checks if the provided repository URL is either an OCI registry or a
    legacy Helm registry. It performs a request to the OCI registry endpoint and also
    checks for the presence of a Helm `index.yaml` file. If neither check identifies the
    repository type, the function defaults to returning `False`.

    Args:
        repo_url (str): The repository URL to be validated.
        headers (dict): The headers to include in the HTTP requests.

    Returns:
        bool: `True` if the repository is an OCI registry, otherwise `False`.
    """
    # Normalize the URL
    repo_url = repo_url.rstrip("/")

    # Check if it's an OCI registry
    try:
        oci_url = f"{repo_url}/v2/"
        response = requests.get(oci_url, headers=headers, timeout=5)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED]:
            return True  # OCI registry detected
    except requests.exceptions.RequestException:
        pass  # Suppress exceptions for this check

    # Check if it's a legacy Helm registry
    try:
        helm_index_url = f"{repo_url}/index.yaml"
        response = requests.head(helm_index_url, headers=headers, timeout=5)
        if response.status_code == HTTPStatus.OK:
            return False  # Legacy Helm registry detected
    except requests.exceptions.RequestException:
        pass  # Suppress exceptions for this check

    # If neither checks succeed, default to not an OCI registry
    return False


def get_auth_headers(creds: Creds, registry: str) -> dict:
    """Gets the authentication headers required for accessing a given registry and repository.

    This function retrieves the credentials associated with a given registry from the `Creds`
    object, and uses them to generate the appropriate HTTP headers for authentication. If
    the registry is Docker Hub (`registry-1.docker.io`), it retrieves a token using the
    Docker Hub's token retrieval flow. Otherwise, it generates a basic authentication header
    by encoding the username and password.

    Args:
        creds (Creds): Object containing the credentials configuration and methods
            to retrieve registry credentials.
        registry (str): The URL of the container registry for which authentication is required.

    Returns:
        dict: A dictionary of HTTP headers to be used for authentication, or an
        empty dictionary if no credentials were available or configured for the
        given registry.
    """
    registry_creds = creds.get_helm_creds(name=registry)
    if registry_creds is None:
        logging.debug(f"no creds for registry: {registry}")
        return {}

    if registry_creds.username and registry_creds.password:
        logging.debug(f"using credentials for: {registry_creds.username}")

    headers = {}

    token = get_registry_token(registry, registry_creds.username, registry_creds.password)
    headers["Authorization"] = f"Bearer {token}"
    return headers


def oci_chart_exists(
    chart: HelmChart,
    headers: dict[str, str],
) -> RC:
    """Checks if an OCI (Open Container Initiative) Helm chart exists in a target registry.

    This function verifies whether a specified Helm chart exists by querying the target
    OCI-compliant registry. The function constructs the manifest URL for the chart by
    taking into account the registry URL, chart name, version, and other parameters. It
    sends a GET request to the constructed URL with necessary headers to determine the
    existence of the chart. If the chart exists, a success response is returned; otherwise,
    an appropriate failure response is provided.

    Args:
        chart (HelmChart): The Helm chart object containing details like the registry,
            repository, chart name, and version.
        headers (Dict[str, str]): Dictionary of HTTP headers to be included in the request.

    Returns:
        RC: A response object indicating whether the chart exists or not, including
            additional context like the HTTP response entity.

    Raises:
        RequestException: If an HTTP-related connection or response issue occurs during
            the GET request.

    """
    # Ensure repo_url has the proper scheme
    repo_url = chart.target_registry
    if not chart.target_registry.startswith(("http://", "https://")):
        repo_url = f"https://{chart.target_registry}"
    repo_path = chart.target_repo.strip("/") + "/" if chart.target_repo else ""

    # Add accept headers for OCI
    oci_headers = headers.copy()
    oci_headers.update(
        {
            "Accept": "application/vnd.oci.image.manifest.v1+json",
            "Accept-Encoding": "gzip",
        }
    )

    # Construct the URL to check for the chart manifest
    manifest_url = (
        f"{repo_url.rstrip('/')}/v2/{repo_path}{chart.chart_name}/manifests/{chart.version}"
    )

    try:
        # Make a GET request to check if the manifest exists
        response = requests.get(manifest_url, headers=oci_headers, timeout=10)

        # A 200 OK response means the chart exists
        if response.status_code == HTTPStatus.OK:
            return RC(ok=True, entity=response)

        # 404 Not Found indicates the chart does not exist
        if response.status_code == HTTPStatus.NOT_FOUND:
            return RC(ok=False, entity=response)

        # Raise an exception for other error codes
        response.raise_for_status()

    except requests.RequestException as e:
        msg = f"Error checking chart existence: {e}"
        logging.exception(msg)
        return RC(ok=False, err=True, type="helm", entity=requests, msg=msg)

    return RC(ok=False, type="helm", entity=response)
