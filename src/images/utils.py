import base64
import logging
import re
from typing import Optional

import requests

from models.rc import RC
from models.resources.image import Image


def image_to_folder_name(image_name: str) -> str:
    """
    Converts an image name into a safe folder name by removing unsafe characters
    and formatting it to be compatible with file systems.

    Args:
        image_name (str): The name of the image, which might include unsafe
            characters or a digest.

    Returns:
        str: A sanitized version of the image name suitable for use as a folder
            name.
    """
    # Remove digest if exists
    if "@" in image_name:
        image_name = image_name.split("@")[0]

    # Replace potentially problematic characters
    safe_name = image_name.replace("/", "_").replace(".", "_").replace(":", "_")

    # Remove any other potentially unsafe characters
    safe_name = "".join(c if c.isalnum() else "_" for c in safe_name)

    # remove potential multiple underscores
    safe_name = re.sub(r"_+", "_", safe_name)

    # Remove any leading or trailing underscores
    safe_name = safe_name.strip("_")

    return safe_name


def check_image_tag_exists(
    image: Image,
    tag: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> RC:
    """
    Checks if a specific Docker image tag exists in a container registry. It handles
    authentication through either basic authentication (username/password) or token-based
    authentication for Docker Hub. The function performs a HEAD request to determine
    if the specified tag is available.

    Args:
        image (Image): An object containing details about the target image, such as
            registry and repository.
        tag (str): The specific tag of the Docker image to check.
        username (Optional[str]): The username for basic authentication if required.
            Defaults to None.
        password (Optional[str]): The password for basic authentication if required.
            Defaults to None.

    Returns:
        RC: An object containing the result of the check. If the image tag exists
            in the registry, the `ok` attribute will be True; otherwise, False.
            Additionally, `msg` and `err` attributes provide further context in
            case of errors or unexpected responses.

    Raises:
        Exception: Any unexpected error encountered during the process is caught
            and logged, and an error response is returned within the RC object.
    """
    try:
        # Construct authentication header if credentials provided
        headers = {
            "Accept": "application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json"  # noqa: E501
        }
        if username and password:
            auth = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {auth}"
            logging.debug("using provided username and password for authentication")
        else:
            logging.debug("no username and password provided for authentication")

        # Special handling for Docker Hub
        repository = image.target_repo
        if image.target_registry == "registry-1.docker.io":
            if "/" not in image.target_repo:
                repository = f"library/{image.target_repo}"
            # Get token for Docker Hub
            auth_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repository}:pull"  # noqa: E501
            token_response = requests.get(auth_url, timeout=5)
            if token_response.status_code == 200:
                token = token_response.json()["token"]
                headers["Authorization"] = f"Bearer {token}"

        # Construct manifest URL
        url = f"https://{image.target_registry}/v2/{repository}/manifests/{tag}"

        # Make request to check if image exists
        response = requests.head(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return RC(ok=True)
        if response.status_code == 404:
            return RC(ok=False, msg=f"image not found: {image.target}")
        if response.status_code == 401:
            return RC(ok=False, msg="unauthenticated", err=True)
        return RC(ok=False, msg=f"unexpected response: {response.status_code}")
    except Exception as e:
        msg = str(e)
        logging.error(msg)
        return RC(ok=False, msg=msg, err=True)
