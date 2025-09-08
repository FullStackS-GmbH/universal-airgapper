import hashlib
import json
import logging
import os
import pathlib
import shutil
from base64 import b64encode
from typing import Optional

import requests

from models.rc import RC


def _cleanup_directory(src_image_dir):
    """
    Cleans up the contents of the specified directory by removing all files and
    subdirectories.

    Args:
        src_image_dir (str or pathlib.Path): The path to the directory whose
            contents need to be removed.

    """
    logging.debug(f"Cleaning up contents of {src_image_dir}")
    for item in pathlib.Path(src_image_dir).glob("*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def _upload_config_blob(config_bytes, config_digest, base_url, headers):
    """
    Uploads a configuration blob to a remote server if it does not already exist.

    The function checks whether the configuration blob identified by the given
    digest exists on the remote server. If it does not exist, the function uploads
    the blob. The function uses a series of HTTP requests to perform the operation,
    including a HEAD request to check for existence, a POST request to initiate
    the upload, and a PUT request to complete the upload.

    Args:
        config_bytes (bytes): The binary data of the configuration blob to upload.
        config_digest (str): The digest of the configuration blob, used for
            identification.
        base_url (str): The base URL of the server to which the blob is to be
            uploaded.
        headers (dict): A dictionary of HTTP headers to include with the requests.

    Raises:
        requests.exceptions.RequestException: If any of the HTTP requests fail.
            This includes connection errors, timeout errors, or HTTP errors
            returned by the server.
    """
    head_url = f"{base_url}/blobs/{config_digest}"
    response = requests.head(head_url, headers=headers, timeout=5)
    if response.status_code == 404:
        upload_url = requests.post(
            f"{base_url}/blobs/uploads/", headers=headers, timeout=10
        ).headers["Location"]
        headers["Content-Type"] = "application/octet-stream"
        requests.put(
            f"{upload_url}&digest={config_digest}",
            headers=headers,
            data=config_bytes,
            timeout=10,
        ).raise_for_status()


def _push_manifest(manifest_json, tgt_image_tag, base_url, headers):
    """
    Pushes a manifest to a remote registry with a specified target image tag.

    This function takes a manifest in JSON format and pushes it to an image repository
    under a target image tag. It sends a PUT request to the manifest endpoint of
    the image repository with the provided headers and manifest content. A timeout
    is set for the operation, and it raises an exception if the response indicates
    a failure.

    Args:
        manifest_json: dict
            The manifest data to be pushed, containing at least a "mediaType" field.
        tgt_image_tag: str
            The target image tag under which the manifest will be stored in the repository.
        base_url: str
            The base URL of the target image repository.
        headers: dict
            The HTTP headers to include in the PUT request. "Content-Type" will
            be automatically set to the "mediaType" field of the manifest if available.

    Returns:
        str:
            The "Docker-Content-Digest" returned in the response headers, or an
            empty string if not present.

    Raises:
        requests.exceptions.RequestException:
            If there is an error during the HTTP request. This includes timeouts
            and errors in the HTTP response (status codes 4xx or 5xx).
    """
    headers["Content-Type"] = manifest_json.get("mediaType", "application/json")
    manifest_url = f"{base_url}/manifests/{tgt_image_tag}"
    response = requests.put(
        manifest_url, headers=headers, json=manifest_json, timeout=10
    )
    response.raise_for_status()
    return response.headers.get("Docker-Content-Digest", "")


def _generate_auth_headers(username, password):
    """

    Generates authentication headers for Basic Auth.

    This function creates a dictionary containing the Authorization header
    required for Basic Authentication, encoded in Base64 format. If either
    the username or password is missing, it returns None.

    Args:
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        dict: A dictionary containing the Authorization header with the
              Basic encoded credentials, or None if either parameter is
              not provided.
    """
    if username and password:
        auth_string = b64encode(f"{username}:{password}".encode()).decode()
        return {"Authorization": f"Basic {auth_string}"}
    return None


def _upload_layer(
    layer_path, base_url, headers, default_content_type="application/octet-stream"
):
    """
    Uploads a binary layer to a specified remote server, ensuring the layer does
    not already exist on the server. Calculates the SHA-256 digest of the layer
    to verify integrity and handles re-upload only if the digest is not found
    on the server.

    Args:
        layer_path (str): The local file path of the binary layer to upload.
        base_url (str): The base URL of the server where the layer is uploaded.
        headers (dict): HTTP headers to include in the requests.
        default_content_type (str): The content type of the binary layer.
            Defaults to "application/octet-stream".

    Returns:
        dict: Metadata of the uploaded layer, including its media type, size,
        and digest.
    """
    with open(layer_path, "rb") as f:
        sha256_hash = hashlib.sha256()
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    layer_digest = f"sha256:{sha256_hash.hexdigest()}"
    logging.debug(f"Layer digest: {layer_digest}")

    # Check existence
    head_url = f"{base_url}/blobs/{layer_digest}"
    response = requests.head(head_url, headers=headers, timeout=5)
    if response.status_code == 404:
        logging.debug(f"Layer {layer_digest} not found, uploading...")
        upload_url = requests.post(
            f"{base_url}/blobs/uploads/", headers=headers, timeout=10
        ).headers["Location"]
        with open(layer_path, "rb") as f:
            headers["Content-Type"] = "application/octet-stream"
            requests.put(
                f"{upload_url}&digest={layer_digest}",
                headers=headers,
                data=f,
                timeout=10,
            ).raise_for_status()
    return {
        "mediaType": default_content_type,
        "size": os.path.getsize(layer_path),
        "digest": layer_digest,
    }


def push_container_image(
    src_image_dir: str,
    tgt_image_name: str,
    tgt_image_tag: str,
    tgt_registry: str = "registry-1.docker.io",
    username: Optional[str] = None,
    password: Optional[str] = None,
    cleanup_src_image_dir: bool = True,
) -> RC:
    """
    Pushes a container image to a specified target registry.

    This function handles uploading a container image along with its associated layers
    and configuration to a target registry. The process involves generating authentication
    headers, uploading image layers and configuration, pushing the manifest, and optionally
    cleaning up the source image directory. It assumes the input image directory contains
    all necessary artifacts (e.g., config.json, manifest.json, layer files).

    Args:
        src_image_dir (str): The source directory containing the container image files.
        tgt_image_name (str): The target image repository name in the registry.
        tgt_image_tag (str): The version tag to assign to the image.
        tgt_registry (str, optional): The URL of the target container registry.
            Defaults to "registry-1.docker.io".
        username (Optional[str], optional): The username for authentication.
            Defaults to None.
        password (Optional[str], optional): The password for authentication.
            Defaults to None.
        cleanup_src_image_dir (bool, optional): Whether to delete the source image
            directory after a successful push. Defaults to True.

    Returns:
        RC: An object containing the status of the operation. If the push is successful,
            the `ok` attribute is True, and the `ref` attribute holds the manifest digest.
            Otherwise, `ok` is False, and the `entity` and `msg` attributes provide
            error details.
    """
    # Constants
    base_url = f"https://{tgt_registry}/v2/{tgt_image_name}"
    default_content_type = "application/vnd.oci.image.layer.v1.tar+gzip"

    # Step 1: Generate authentication headers
    headers = _generate_auth_headers(username, password) or {}

    config_path = os.path.join(src_image_dir, "config.json")
    manifest_path = os.path.join(src_image_dir, "manifest.json")

    manifest_json = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_json = json.load(f)

    # Step 2: Upload layers
    layers = []
    try:
        logging.debug("Uploading image layers from manifest.json")
        for layer in manifest_json.get("layers", []):
            layer_sha = layer.get("digest")
            layer_file = layer_sha.replace(":", "_")
            layer_path = os.path.join(src_image_dir, layer_file)
            if os.path.isfile(layer_path):
                layers.append(
                    _upload_layer(layer_path, base_url, headers, default_content_type)
                )
    except Exception as e:
        msg = f"Error uploading layers for: {tgt_image_name}"
        logging.error(msg)
        return RC(ok=False, entity=e, msg=msg)

    # Step 3: Generate or load configuration
    try:
        with open(config_path, "rb") as f:
            config_bytes = f.read()
        config_digest = f"sha256:{hashlib.sha256(config_bytes).hexdigest()}"
        # Step 4: Upload configuration blob
        _upload_config_blob(config_bytes, config_digest, base_url, headers)
    except Exception as e:
        msg = f"Error uploading config for: {tgt_image_name}"
        logging.error(msg)
        return RC(ok=False, entity=e, msg=msg)

    # Step 5: Push manifest
    try:
        manifest_digest = _push_manifest(
            manifest_json, tgt_image_tag, base_url, headers
        )
    except Exception as e:
        msg = f"Error uploading manifest for: {tgt_image_name}"
        logging.error(msg)
        return RC(ok=False, entity=e, msg=msg)

    # Step 6: Clean up directory (optional)
    if cleanup_src_image_dir:
        _cleanup_directory(src_image_dir)

    return RC(ok=True, ref=manifest_digest)
