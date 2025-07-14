import hashlib
import json
import logging
import os
from typing import Dict, Literal, Optional

import requests

from charts.utils import extract_chart_info
from models.rc import RC

RepoType = Literal["oci", "nexus"]


def push_helm_chart(
    chart_path: str,
    repo_url: str,
    repo_type: Optional[RepoType] = None,
    repo_path: Optional[str] = None,
    headers: Optional[dict] = None,
    cleanup_chart: bool = True,
) -> RC:
    """
    Pushes a Helm chart to a specified repository.

    This function handles the process of uploading a Helm chart from a .tgz file to a
    repository. It supports different repository types and can optionally clean up
    the chart file after pushing. Additionally, metadata of the chart is extracted
    and associated with the return value.

    Args:
        chart_path (str): Path to the Helm chart file (.tgz archive) to be pushed.
        repo_url (str): URL of the repository to which the Helm chart is to be uploaded.
        repo_type (Optional[RepoType]): Type of the repository (e.g., "oci"). Defaults to None.
        repo_path (Optional[str]): Path inside the repository where the chart will be placed.
            Defaults to None.
        headers (Optional[dict]): Headers to be included in the request when pushing the chart.
            Defaults to None.
        cleanup_chart (bool): Indicates whether the chart file should be removed after
            successfully uploading. Defaults to True.

    Returns:
        RC: Result code containing the status of the operation, with metadata of the pushed chart
            if successful.
    """
    if not os.path.exists(chart_path):
        return RC(ok=False, type="helm", msg=f"Chart file not found at {chart_path}")

    if not chart_path.endswith(".tgz"):
        return RC(ok=False, type="helm", msg=f"Chart file must be a .tgz archive, got {chart_path}")

    # Extract chart metadata
    chart_info = extract_chart_info(chart_path)

    rc = RC(ok=True)
    match repo_type:
        case "oci":
            rc = _push_oci_chart(chart_path, chart_info, repo_url, headers, repo_path)
        case "nexus":
            rc = _push_nexus_chart(chart_path, repo_path, chart_info, repo_url, headers)

    if cleanup_chart:
        try:
            os.remove(chart_path)
        except OSError as e:
            logging.warning(f"Warning: Failed to remove chart file {chart_path}: {e}")

    rc.entity = chart_info
    return rc


def _push_nexus_chart(
    chart_path: str,
    repo_path: str,
    chart_info: Dict[str, str],
    repo_url: str,
    headers: Dict[str, str],
) -> RC:
    """
    Pushes a Helm chart to a Nexus repository.

    This function uploads a Helm chart `.tgz` file to a Nexus repository using
    the provided repository URL and headers for authentication.

    Args:
        chart_path (str): Path to the Helm chart file to be pushed.
        repo_path (str): name of the repository.
        chart_info (Dict[str, str]): Metadata about the chart, such as its name and version.
        repo_url (str): Base URL of the Nexus repository.
        headers (Dict[str, str]): HTTP headers for authentication.

    Returns:
        RC: An RC object indicating the success or failure of the operation.
    """
    # Ensure repo_url has proper scheme
    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    # Construct the full upload URL
    upload_url = f"{repo_url.rstrip('/')}/repository/{repo_path}/"

    try:
        # Read chart data
        with open(chart_path, "rb") as f:
            # Upload the chart to Nexus
            response = requests.post(
                upload_url,
                headers=headers,
                files={"file": f},
                timeout=10,
            )
            response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Error pushing chart to Nexus repository: {e}"
        logging.error(msg)
        return RC(ok=False, err=True, type="helm", msg=msg)

    return RC(
        ok=True,
        ref=f"{repo_path}/{chart_info['name']}/{chart_info['version']}",
        type="helm",
        msg=f"Successfully pushed {chart_info['name']}:{chart_info['version']} to Nexus.",
    )


def _push_oci_chart(
    chart_path: str,
    chart_info: Dict[str, str],
    repo_url: str,
    headers: Dict[str, str],
    repo_path: Optional[str] = None,
) -> RC:
    """
    Pushes a Helm chart to an OCI-compliant image repository.

    This function uploads a Helm chart to an OCI-compliant image repository
    at a specified URL. It involves calculating the chart's digest, creating
    a configuration blob, uploading both the chart blob and configuration blob,
    and finally generating and pushing a manifest. The function utilizes the
    OCI Image Format Specifications to ensure compatibility.

    Args:
        chart_path (str): Path to the Helm chart file (e.g., `.tgz` file) to be pushed.
        chart_info (Dict[str, str]): Metadata about the chart, including its name and version.
        repo_url (str): Base URL of the OCI repository.
        headers (Dict[str, str]): HTTP headers for authentication or additional metadata.
        repo_path (Optional[str]): Optional repository path to be appended to the full URL.

    Returns:
        RC: An object representing the result of the push operation. Contains whether
            it was successful, a reference (e.g., digest) if applicable, the type
            (always "helm"), and a message with additional details.

    Raises:
        requests.RequestException: In case of HTTP request failures during one of the
            upload steps.
    """
    # Ensure repo_url has proper scheme
    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    # Construct repository path
    if repo_path:
        chart_repo_path = f"{repo_path}/{chart_info['name']}"
    else:
        chart_repo_path = chart_info["name"]

    # Calculate chart digest
    with open(chart_path, "rb") as f:
        chart_data = f.read()
        sha256_hash = hashlib.sha256(chart_data).hexdigest()
        chart_digest = f"sha256:{sha256_hash}"

    # Create config
    config = {
        "mediaType": "application/vnd.cncf.helm.config.v1+json",
        "schemaVersion": 2,
        "software": {
            "name": chart_info["name"],
            "version": chart_info["version"],
            "type": "helm",
        },
    }
    config_bytes = json.dumps(config).encode()
    config_digest = f"sha256:{hashlib.sha256(config_bytes).hexdigest()}"

    try:
        # Upload config blob
        upload_url = f"{repo_url.rstrip('/')}/v2/{chart_repo_path}/blobs/uploads/"
        response = requests.post(upload_url, headers=headers, timeout=10)
        response.raise_for_status()

        upload_location = response.headers["Location"]
        headers_with_type = headers.copy()
        headers_with_type["Content-Type"] = "application/json"
        response = requests.put(
            f"{upload_location}&digest={config_digest}",
            headers=headers_with_type,
            data=config_bytes,
            timeout=10,
        )
        response.raise_for_status()

        # Upload chart blob
        response = requests.post(upload_url, headers=headers, timeout=10)
        response.raise_for_status()

        upload_location = response.headers["Location"]
        headers_with_type = headers.copy()
        headers_with_type["Content-Type"] = "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
        response = requests.put(
            f"{upload_location}&digest={chart_digest}",
            headers=headers_with_type,
            data=chart_data,
            timeout=10,
        )
        response.raise_for_status()

        # Create and push manifest
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.cncf.helm.config.v1+json",
                "size": len(config_bytes),
                "digest": config_digest,
            },
            "layers": [
                {
                    "mediaType": "application/vnd.cncf.helm.chart.content.v1.tar+gzip",
                    "size": len(chart_data),
                    "digest": chart_digest,
                }
            ],
        }

        headers_with_type = headers.copy()
        headers_with_type["Content-Type"] = "application/vnd.oci.image.manifest.v1+json"
        manifest_url = (
            f"{repo_url.rstrip('/')}/v2/{chart_repo_path}/manifests/{chart_info['version']}"
        )
        response = requests.put(manifest_url, headers=headers_with_type, json=manifest, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Error pushing chart to OCI repository: {e}"
        logging.error(msg)
        return RC(ok=False, type="helm", msg=msg)

    return RC(
        ok=True,
        ref=response.headers.get("Docker-Content-Digest", ""),
        type="helm",
        msg=f"{repo_url.rstrip('/')}/{chart_repo_path}:{chart_info['version']}",
    )
