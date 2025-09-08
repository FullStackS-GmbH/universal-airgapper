import json
import logging
import os
from typing import Optional

import requests

from cli.utils import get_registry_token
from models.rc import RC

SUPPORTED_MANIFEST_TYPES = [
    "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.oci.image.index.v1+json",
]


def pull_container_image(
    image_name: str,
    tag: str,
    architecture: str = "amd64",
    registry: str = "registry-1.docker.io",
    username: Optional[str] = None,
    password: Optional[str] = None,
    output_dir: str = "./images",
) -> RC:
    """
    Pulls a container image from a specified container registry, authenticates if necessary,
    fetches its manifest, and downloads the image layers and configuration.

    :param image_name: The name of the container image to pull.
    :param tag: The tag for the image, such as 'latest' or a version number.
    :param architecture: The target system architecture for the image (default: "amd64").
    :param registry: The container registry to pull the image from
        (default: "registry-1.docker.io").
    :param username: The username for registry authentication. Optional.
    :param password: The password for registry authentication. Optional.
    :param output_dir: The local directory where the image and its layers will be saved
        (default: "./images").
    :return: The path to the directory where the image was saved.

    :raises ValueError: If the manifest type of the image is unsupported by the
        underlying implementation.

    Examples:
        Example usage for pulling a container image successfully:

        >>> pull_container_image(
        ...    image_name="ubuntu",
        ...    tag="22.04",
        ...    architecture="amd64",
        ...    output_dir="/tmp/ubuntu_image"
        ... )
        '/tmp/ubuntu_image'

        If the image is pulled from DockerHub's 'library' namespace:

        >>> pull_container_image(image_name="alpine", tag="3.17")
        './images'

        Example with authentication for a private registry:

        >>> pull_container_image(
        ...    image_name="myorg/private-image",
        ...    tag="v1.0.0",
        ...    registry="my-privateregistry.com",
        ...    username="user",
        ...    password="pass",
        ...    output_dir="/var/images"
        ... )
        '/var/images'
    """
    logging.debug(
        f"Starting pull for {registry}/{image_name}:{tag} (arch: {architecture})"
    )

    if registry == "registry-1.docker.io" and "/" not in image_name:
        image_name = f"library/{image_name}"
        logging.debug(f"Using official image path: {image_name}")

    headers = _authenticate_with_registry(registry, image_name, username, password)

    # Fetch image manifest
    try:
        manifest_url = f"https://{registry}/v2/{image_name}/manifests/{tag}"
        manifest = _fetch_manifest(manifest_url, headers)
    except requests.exceptions.RequestException as e:
        msg = f"could not fetch image manifest for {image_name}:{tag} from {registry} -> {e}"
        logging.error(msg)
        return RC(ok=False, msg=msg)

    # Handle multi-arch manifests
    if manifest.get("mediaType") in [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
    ]:
        manifest = _select_matching_manifest(
            manifest, architecture, registry, image_name, headers
        )

    # Verify and store manifest
    if manifest.get("mediaType") not in SUPPORTED_MANIFEST_TYPES:
        return RC(
            ok=False, msg=f"Unsupported manifest type: {manifest.get('mediaType')}"
        )
    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # Download layers
    logging.debug(f"Downloading {len(manifest['layers'])} layers")
    try:
        for i, layer in enumerate(manifest["layers"], 1):
            layer_path = os.path.join(output_dir, layer["digest"].replace(":", "_"))
            _download_blob(
                layer["digest"],
                registry,
                image_name,
                headers,
                layer_path,
                expected_size=layer.get("size"),
            )
            logging.debug(
                f"Layer {i}/{len(manifest['layers'])} downloaded: {layer['digest']}"
            )
    except requests.exceptions.RequestException as e:
        msg = f"could not fetch image layer {image_name}:{tag} from {registry} -> {e}"
        logging.error(msg)
        return RC(ok=False, msg=msg)

    # Download config blob
    try:
        if "config" in manifest:
            config_path = os.path.join(output_dir, "config.json")
            _download_blob(
                manifest["config"]["digest"], registry, image_name, headers, config_path
            )
    except requests.exceptions.RequestException as e:
        msg = f"could not fetch config manifest for {image_name}:{tag} from {registry} -> {e}"
        logging.error(msg)
        return RC(ok=False, msg=msg)

    msg = f"Image pull completed successfully to: {output_dir}"
    logging.debug(msg)
    return RC(ok=True, ref=output_dir, msg=msg)


def _authenticate_with_registry(
    registry: str, image_name: str, username: Optional[str], password: Optional[str]
) -> dict:
    """
    Authenticate with a container image registry.

    This function generates authorization headers required for fetching
    container image manifests. It supports both Docker Hub authentication
    (using a token) or basic authentication using username and password. If no
    authentication details are provided for Docker Hub, the function fetches a
    public access token.

    :param registry: The registry URL or identifier against which the authentication
        needs to be performed (e.g., 'registry-1.docker.io').
    :type registry: str
    :param image_name: The name of the image in the specified registry. Required
        for Docker Hub token retrieval (e.g., 'library/ubuntu').
    :type image_name: str
    :param username: The username for authentication. Provide if basic authentication
        is required or for private Docker Hub repositories.
        Optional parameter.
    :type username: Optional[str]
    :param password: The password for authentication. Must be specified along with
        username for basic authentication or private Docker Hub repositories.
        Optional parameter.
    :type password: Optional[str]
    :return: A dictionary containing the headers to be used for subsequent API
        requests, which includes the generated authentication information.
    :rtype: dict

    :Example:

    >>> _authenticate_with_registry(
    ...     registry="registry-1.docker.io",
    ...     image_name="library/ubuntu",
    ...     username=None,
    ...     password=None
    ... )
    {'Accept': 'application/vnd.docker.distribution.manifest.v2+json,...',
     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJle...'}

    >>> _authenticate_with_registry(
    ...     registry="my-private-registry.example.com",
    ...     image_name="myimage:tag",
    ...     username="myuser",
    ...     password="mypassword"
    ... )
    {'Accept': 'application/vnd.docker.distribution.manifest.v2+json,...',
     'Authorization': 'Basic bXl1c2VyOm15cGFzc3dvcmQ='}
    """
    headers = {
        "Accept": ",".join(
            SUPPORTED_MANIFEST_TYPES
            + [
                "application/vnd.oci.image.index.v1+json",
                "application/vnd.docker.distribution.manifest.list.v2+json",
            ]
        )
    }

    full_image_name = registry + "/" + image_name
    token = get_registry_token(full_image_name, username, password)
    if token == "":
        # empty token means, fetchin was successfull without auth. so return empty header
        return headers
    headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_manifest(manifest_url: str, headers: dict) -> dict:
    """
    Fetches a manifest from a provided URL using HTTP GET request.

    The function sends a GET request to the specified `manifest_url`, including
    any headers provided. It then validates the HTTP response for errors and
    parses the response body as JSON.

    :param manifest_url: The URL from which the manifest will be fetched.
    :param headers: A dictionary containing HTTP headers to include in the GET
        request.
    :return: Returns the manifest parsed as a dictionary.

    :example:
        ::

            manifest_url = "https://api.example.com/manifest"
            headers = {"Authorization": "Bearer your_token"}
            manifest = fetch_manifest(manifest_url, headers)

            # Example output
            {
                "version": "1.0",
                "components": ["component1", "component2"]
            }
    """
    logging.debug(f"Fetching manifest from: {manifest_url}")
    response = requests.get(manifest_url, headers=headers, timeout=5)
    response.raise_for_status()
    return response.json()


def _select_matching_manifest(
    manifest: dict, architecture: str, registry: str, image_name: str, headers: dict
) -> dict:
    """
    Selects and returns a matching image manifest based on the given architecture.

    This function processes a multi-architecture manifest and retrieves the first
    sub-manifest that corresponds to the specified architecture. A sub-manifest is
    fetched from the provided registry for the matching architecture using the
    manifest's digest. It ensures compatibility by identifying the correct platform
    for the given architecture.

    :param manifest: Dictionary containing the multi-architecture image manifest.
    :param architecture: The target architecture to match (e.g., "amd64", "arm64").
    :param registry: The Docker registry URL where the manifest can be fetched.
    :param image_name: The name of the Docker image including potential paths.
    :param headers: Dictionary of HTTP headers required for the Docker registry.
    :return: A dictionary representing the manifest for the specific architecture.
    :raises ValueError: Raised when no manifest matches the given architecture.

    Example usage:

      manifest = {
          "manifests": [
              {
                  "platform": {"architecture": "amd64"},
                  "digest": "sha256:exampledigest1"
              },
              {
                  "platform": {"architecture": "arm64"},
                  "digest": "sha256:exampledigest2"
              }
          ]
      }
      architecture = "arm64"
      registry = "example.registry.io"
      image_name = "my-repo/my-image"
      headers = {"Authorization": "Bearer token"}

      result = select_matching_manifest(
          manifest=manifest,
          architecture=architecture,
          registry=registry,
          image_name=image_name,
          headers=headers
      )
      # Output: The function will return the fetched manifest for "arm64" architecture.

    """
    logging.debug("Processing multi-arch manifest")
    for candidate in manifest["manifests"]:
        if candidate["platform"]["architecture"] == architecture:
            logging.debug(f"Found matching manifest for architecture: {architecture}")
            sub_manifest_url = (
                f"https://{registry}/v2/{image_name}/manifests/{candidate['digest']}"
            )
            return _fetch_manifest(sub_manifest_url, headers)
    raise ValueError(f"No matching manifest found for architecture: {architecture}")


def _download_blob(
    digest: str,
    registry: str,
    image_name: str,
    headers: dict,
    output_path: str,
    expected_size: Optional[int] = None,
):
    blob_download_url = f"https://{registry}/v2/{image_name}/blobs/{digest}"
    logging.debug(f"Downloading blob: {digest}")
    response = requests.get(blob_download_url, headers=headers, stream=True, timeout=5)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    if expected_size is not None:
        actual_size = os.path.getsize(output_path)
        if actual_size != expected_size:
            raise ValueError(
                f"Blob size mismatch for {digest}. Expected {expected_size}, got {actual_size}"
            )
