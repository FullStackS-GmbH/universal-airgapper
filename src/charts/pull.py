import os
import tarfile
import tempfile
from typing import Dict, Optional

import requests
import yaml

from charts.utils import is_oci_registry
from models.rc import RC


def pull_helm_chart(
    chart_path: str,
    version: str,
    registry_url: str,
    output_dir: str,
    headers: Optional[Dict[str, str]] = None,
) -> RC:
    """
    Pulls a Helm chart from either an OCI registry or a traditional registry based on the
    registry type and saves it in the specified output directory.

    This function determines whether the given registry is an OCI type or a traditional
    Helm repository by using the provided registry URL and headers. Depending on the type
    of registry, the appropriate pull method is invoked to pull and store the Helm chart.

    Args:
        chart_path (str): The path or name of the Helm chart to pull.
        version (str): The version of the Helm chart to pull.
        registry_url (str): URL of the Helm chart's registry.
        output_dir (str): Directory where the Helm chart will be stored.
        headers (Optional[Dict[str, str]]): Optional headers for authenticating the request.

    Returns:
        RC: Return code or result object indicating the success or failure of the pull operation.

    Raises:
        OSError: If the output directory cannot be created.
        SomeException: If other internal exceptions occur in the called pull methods.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Detect if it's an OCI registry
    is_oci = is_oci_registry(f"https://{registry_url}", headers)

    if is_oci:
        return _pull_oci_chart(chart_path, version, registry_url, output_dir, headers)
    return _pull_traditional_chart(chart_path, version, registry_url, output_dir, headers)


def _pull_traditional_chart(
    chart_path: str,
    version: str,
    repo_url: str,
    output_dir: str,
    headers: Dict[str, str],
) -> RC:
    """
    Fetches and saves a Helm chart from a specified repository.

    This function retrieves a specified Helm chart in a particular version from
    a given Helm repository URL. The chart is downloaded and stored locally in
    the specified output directory.

    Args:
        chart_path (str): The name of the chart to retrieve from the repository.
        version (str): The specific version of the chart to fetch.
        repo_url (str): The URL of the helm repository from which the chart is
            fetched.
        output_dir (str): Directory path where the downloaded chart will be saved.
        headers (Dict[str, str]): HTTP headers to be included when making requests
            to the repository.

    Returns:
        RC: An object containing success status and information about the saved
        chart file.

    Raises:
        ValueError: If the chart cannot be found in the repository or if the
            specified version isn't available in the charts.
        requests.exceptions.RequestException: If there is any issue during the
            HTTP requests to fetch the chart index or the chart itself.
    """
    # Ensure repo_url ends with proper scheme
    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    # Fetch repository index
    index_url = f"{repo_url.rstrip('/')}/index.yaml"
    response = requests.get(index_url, headers=headers, timeout=5)
    response.raise_for_status()

    # Parse index
    index = yaml.safe_load(response.text)

    # Find chart entry
    if chart_path not in index["entries"]:
        raise ValueError(f"Chart {chart_path} not found in repository")

    # Find specific version
    chart_entry = None
    for entry in index["entries"][chart_path]:
        if entry["version"] == version:
            chart_entry = entry
            break

    if not chart_entry:
        raise ValueError(f"Version {version} not found for chart {chart_path}")

    # Download chart
    chart_url = chart_entry["urls"][0]
    if not chart_url.startswith("http"):
        chart_url = f"{repo_url.rstrip('/')}/{chart_url}"

    response = requests.get(chart_url, headers=headers, timeout=5)
    response.raise_for_status()

    # Save chart
    output_file = os.path.join(output_dir, f"{chart_path}-{version}.tgz")
    with open(output_file, "wb") as f:
        f.write(response.content)

    return RC(ok=True, ref=output_file)


def _pull_oci_chart(
    chart_path: str,
    version: str,
    repo_url: str,
    output_dir: str,
    headers: Dict[str, str],
) -> RC:
    """
    Pulls an OCI-compliant Helm chart from a remote OCI registry and assembles it into a
    compressed tarball archive saved to the specified output directory.

    Args:
        chart_path: The path to the Helm chart in the OCI registry.
        version: The version of the Helm chart to pull.
        repo_url: The base URL of the OCI registry hosting the chart.
                  If the scheme is missing, HTTPS will be used by default.
        output_dir: The directory where the resulting chart archive will be saved.
        headers: A dictionary of HTTP headers to include in requests.

    Returns:
        RC: A result object containing a success indicator and a reference to the
            generated output file.

    Raises:
        TypeError: If any provided arguments are of an incompatible type.
        requests.exceptions.RequestException: If there is an error in HTTP communication.
        json.JSONDecodeError: If the manifest cannot be parsed as valid JSON.
        KeyError: If the OCI manifest is missing required keys or layers.
        OSError: If any file or directory operation fails during chart extraction
                 and assembly.
    """
    # Ensure repo_url has proper scheme
    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    # Add accept headers for OCI
    oci_headers = headers.copy()
    oci_headers.update(
        {
            "Accept": "application/vnd.oci.image.manifest.v1+json",
            "Accept-Encoding": "gzip",
        }
    )

    # Get manifest
    manifest_url = f"{repo_url.rstrip('/')}/v2/{chart_path}/manifests/{version}"
    response = requests.get(manifest_url, headers=oci_headers, timeout=5)
    response.raise_for_status()

    manifest = response.json()

    # Download layers
    with tempfile.TemporaryDirectory() as temp_dir:
        for layer in manifest["layers"]:
            layer_digest = layer["digest"]
            layer_url = f"{repo_url.rstrip('/')}/v2/{chart_path}/blobs/{layer_digest}"

            response = requests.get(layer_url, headers=headers, timeout=5)
            response.raise_for_status()

            layer_file = os.path.join(temp_dir, layer_digest.replace(":", "_"))
            with open(layer_file, "wb") as f:
                f.write(response.content)

        # Create final chart archive
        output_file = os.path.join(output_dir, f"{chart_path}-{version}.tgz")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Combine layers into final chart
        with tarfile.open(output_file, "w:gz") as tar:
            for layer_file in os.listdir(temp_dir):
                layer_path = os.path.join(temp_dir, layer_file)
                with tarfile.open(layer_path, "r:*") as layer_tar:
                    for member in layer_tar.getmembers():
                        content = layer_tar.extractfile(member)
                        if content:
                            tar.addfile(member, content)

    return RC(ok=True, ref=output_file)
