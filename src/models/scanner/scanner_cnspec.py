import json
import logging
import os
import subprocess

from models.config.config_scanner_cnspec import ConfigCnspecScanner
from models.creds.creds_scanner import CredsScanner
from models.resources.image import Image
from models.scanner.scanner import Scanner
from models.scanner.scanner_result import ScannerResult


class ScannerCnspec(Scanner):
    """Represents a scanner for container security assessments using the Cnspec tool."""

    def __init__(self, credentials: CredsScanner, config: ConfigCnspecScanner):
        super().__init__(credentials=credentials, config=config, name=config.name)
        self.token = credentials.password
        self.config: ConfigCnspecScanner = config

    #    def _prepare_credentials(self):
    #        """TBD"""
    #        pass

    def scan_image(
        self,
        image: Image,
        tag: str,
        registry_username: str,
        registry_password: str,
    ) -> ScannerResult:
        """Scans a container image for vulnerabilities using the `cnspec` tool and
        returns a scanning result in the form of a `ScannerResult` object.

        The method authenticates using environment variables for the `cnspec` tool
        and invokes the external tool via a subprocess. The results of the scan
        are returned in a parsed and structured format. If any errors occur during
        the process, including tool errors or exceptions, they are captured and
        returned within the `ScannerResult` object.

        Args:
            image (Image): The container image to scan.
            tag (str): The specific tag of the container image to scan.
            registry_username (str): The username required for accessing private
                container image registries, if applicable.
            registry_password (str): The password required for accessing private
                container image registries, if applicable.

        Returns:
            ScannerResult: An object encapsulating the success or failure of
            the scan, along with the results or error messages.

        Raises:
            None: This method captures all exceptions internally and includes
            the error details in the `ScannerResult`.
        """
        try:
            env = os.environ.copy()
            env["MONDOO_CONFIG_BASE64"] = self.token  # authenticate
            result = subprocess.run(
                " ".join(
                    [
                        "cnspec",
                        "vuln",
                        "docker",
                        f"{image.source}:{tag}",
                        "--output json",
                    ]
                ),
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=600,
                shell=True,
            )
            if result.returncode != 0:
                return ScannerResult(
                    ok=False,
                    msg=f"cnspec error [{result.returncode}]: {result.stderr.strip()}",
                )
            json_result = json.loads(result.stdout)
            return self.cnspec_2_scanner_result(json_result)
        except Exception as e:
            logging.exception(str(2))
            return ScannerResult(ok=False, msg=f"cnspec error: {e!s}")
