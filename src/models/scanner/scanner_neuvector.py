import json
import logging
from time import sleep

import requests

from models.config.config_scanner_neuvector import ConfigNeuvectorScanner
from models.creds.creds_scanner import CredsScanner
from models.resources.image import Image
from models.scanner.scanner import Scanner
from models.scanner.scanner_result import ScannerResult


class ScannerNeuVector(Scanner):
    """
    Provides functionalities to interact with the NeuVector scanning API for
    conducting image vulnerability scans and analyzing scan results.

    The class serves as an interface for integrating with the NeuVector API,
    managing connections, authentication tokens, and handling actions like
    image vulnerability scanning. It processes the retrieved results to
    determine whether vulnerabilities exceed configured thresholds.

    Attributes:
        token (str): Authentication token to interact with the NeuVector API.
        config (ConfigNeuvectorScanner): Configuration settings specific to
            the NeuVector scanner, including hostname, port, and threshold levels.
        endpoint (str): Fully qualified endpoint URL derived from the hostname
            and port specified in the configuration.
    """

    def __init__(self, credentials: CredsScanner, config: ConfigNeuvectorScanner):
        super().__init__(credentials=credentials, config=config, name=config.name)
        self.token = ""
        self.config: ConfigNeuvectorScanner = config
        self.endpoint = f"{config.hostname}:{config.port}"

    def validate_connection(self) -> bool:
        """
        Validates the connection to a configured endpoint.

        This method sends a DELETE request to the endpoint specified in the
        `self.endpoint` property to validate its availability and configuration.
        The request expects a specific response format to determine if the endpoint
        is functional. If the response does not match the expected format, it
        determines that the connection is invalid.

        Returns:
            bool: True if the connection to the endpoint is validated successfully,
            otherwise False.
        """
        headers = {"Content-Type": "application/json"}

        response = requests.delete(
            url=f"https://{self.endpoint}",
            headers=headers,
            verify=self.config.verify_tls,
            timeout=3,
        )
        # expected answer
        # {"code":1,"error":"URL not found","message":"URL not found"}
        response_json = response.json()
        if not response_json.get("code", 0) == 1:
            return False
        return True

    def invalidate_nv_token(self) -> bool:
        """
        Invalidates the currently active NV token from the authentication service.

        This function sends a DELETE request to the authentication endpoint to revoke
        the active token. It utilizes the token stored in the instance and ensures that
        TLS verification is respected according to the instance's configuration. The
        operation's success is determined by the status of the HTTP response.

        Returns:
            bool: Indicates whether the NV token was successfully invalidated. Returns
            False if the response status is not OK or the request fails.
        """
        headers = {"Content-Type": "application/json", "X-Auth-Token": self.token}

        response = requests.delete(
            url=f"https://{self.endpoint}/v1/auth",
            headers=headers,
            verify=self.config.verify_tls,
            timeout=3,
        )
        if not response.ok:
            return False
        return True

    def fetch_nv_token(self) -> bool:
        """
        Fetches a new API token from the endpoint using provided credentials.

        This method sends a POST request to the authentication endpoint with the
        supplied username and password to obtain a new API token. The token is
        stored in the `self.token` attribute upon successful request.

        Raises:
            requests.exceptions.RequestException: If the request fails due to
                network-related issues or other exceptions.

        Returns:
            bool: True if the token is successfully fetched and stored, False
                otherwise.
        """
        headers = {"Content-Type": "application/json"}

        # fetch API token payload
        payload = {
            "password": {
                "username": self.credentials.username,
                "password": self.credentials.password,
            }
        }
        response = requests.post(
            url=f"https://{self.endpoint}/v1/auth",
            headers=headers,
            data=json.dumps(payload),
            verify=self.config.verify_tls,
            timeout=10,
        )
        if response.ok:
            json_response = response.json()
            self.token = json_response["token"]["token"]
            return True
        return False

    def scan_image(
        self,
        image: Image,
        tag: str,
        registry_username: str,
        registry_password: str,
    ) -> ScannerResult:
        """
        Scans a container image against a configured scanner and returns the results.

        This method performs the scanning of a container image for vulnerabilities
        or other issues by interacting with the scanner API. It uses the provided
        tag, registry credentials, and image details to request a scan and processes
        the response. If an error occurs during the scanning process, it
        handles the error and provides an appropriate result. The method retries
        the request multiple times in case of no response before timing out.

        Args:
            image (Image): The container image to be scanned, including details
                such as the source registry and repository.
            tag (str): The specific tag of the container image to scan.
            registry_username (str): The username for authentication with the
                container image registry.
            registry_password (str): The password for authentication with the
                container image registry.

        Returns:
            ScannerResult: The result of the scan, including its success status
                and any relevant messages.

        Raises:
            Exception: If an unexpected error occurs, it captures and returns the
                exception message in the resulting ScannerResult.
        """
        if not self.fetch_nv_token():
            return ScannerResult(ok=False, msg="could not fetch token")

        headers = {"Content-Type": "application/json", "X-Auth-Token": self.token}
        payload = {
            "request": {
                "registry": f"https://{image.source_registry}",
                "username": registry_username,
                "password": registry_password,
                "repository": image.source_repo,
                "tag": tag,
            }
        }

        cnt = 0
        try:
            logging.debug(f"requesting scan for {image.source_repo}:{tag}")
            while cnt < 10:
                cnt += 1
                logging.debug(f"[{cnt}] waiting for response...")
                response = requests.post(
                    url=f"https://{self.endpoint}/v1/scan/repository",
                    headers=headers,
                    data=json.dumps(payload),
                    verify=self.config.verify_tls,
                    timeout=60,
                )

                if response.ok and response.status_code < 300:
                    return self.neuvector_2_scanner_result(response.json()["report"])
                if response.status_code > 400:
                    return ScannerResult(
                        ok=False, msg=f"scan error [{response.status_code}]: {response.text}"
                    )
                sleep(5)
            return ScannerResult(ok=False, msg="exceeded scan timeout")
        except Exception as e:
            return ScannerResult(ok=False, msg=str(e))
        finally:
            if not self.invalidate_nv_token():
                logging.error("could not invalidate token")
