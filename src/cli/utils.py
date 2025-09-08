from typing import Optional, Tuple

import requests
from requests import RequestException


def parse_docker_image(image_str: str) -> Tuple[str, str, str]:
    """
    Parses a Docker image string into (registry, image, tag).
    Example inputs:
      - 'ubuntu'
      - 'ubuntu:20.04'
      - 'myregistry.com/user/app:1.2.3'
      - 'ghcr.io/org/image'
    """
    tag = "latest"
    if ":" in image_str and "/" in image_str.split(":")[-1]:
        # colon is part of hostname (e.g. localhost:5000)
        image_part = image_str
    else:
        if ":" in image_str:
            image_str, tag = image_str.rsplit(":", 1)
        image_part = image_str

    parts = image_part.split("/")
    if len(parts) == 1:
        registry = "docker.io"
        image = parts[0]
    elif len(parts) == 2:
        registry = "docker.io"
        image = "/".join(parts)
    else:
        registry = parts[0]
        image = "/".join(parts[1:])

    return registry, image, tag


def get_registry_token(
    image: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Gets a registry token for Docker image authentication.

    This function triggers an authentication process with a Docker registry
    to retrieve an authentication token required for accessing the registry.
    It handles the WWW-Authenticate header challenge in a 401 unauthorized
    response and fetches a token from the specified auth endpoint.

    Parameters:
        image: str
            The Docker image name and tag in the format "registry/image:tag".
        username: Optional[str]
            The username for the Docker registry. Default is None for no authentication.
        password: Optional[str]
            The password for the Docker registry. Default is None for no authentication.

    Returns:
        str: The authentication token required to access the registry.

    Raises:
        Exception: If the initial request to trigger the authentication process
        does not return a 401 status code, or if an unsupported authentication
        scheme is encountered in the response, or if token fetching fails.
    """
    parsed_image = parse_docker_image(image_str=image)

    # Step 1: Trigger 401 to get the auth challenge
    test_url = (
        f"https://{parsed_image[0]}/v2/{parsed_image[1]}/manifests/{parsed_image[2]}"
    )
    headers = {
        "Accept": (
            "application/vnd.docker.distribution.manifest.v2+json,"
            "application/vnd.oci.image.index.v1+json,"
            "application/vnd.oci.image.manifest.v1+json"
        )
    }
    response = requests.get(test_url, headers=headers, timeout=5)
    if response.status_code == 200:
        return ""
    if response.status_code != 401:
        raise RequestException(
            f"Expected 401 response, got {response.status_code}: {response.text}"
        )

    www_auth = response.headers.get("WWW-Authenticate", "")
    if not www_auth.startswith("Bearer"):
        raise RequestException(f"Unsupported authentication scheme: {www_auth}")

    # Step 2: Parse auth challenge
    parts = dict(
        kv.strip().split("=") for kv in www_auth.replace("Bearer ", "").split(",")
    )
    realm = parts["realm"].strip('"')
    service = parts["service"].strip('"')
    scope = parts["scope"].strip('"')

    # Step 3: Fetch the token
    params = {"service": service, "scope": scope}
    auth = (username, password) if username and password else None
    token_response = requests.get(realm, params=params, auth=auth, timeout=5)
    token_response.raise_for_status()

    return token_response.json()["token"]
