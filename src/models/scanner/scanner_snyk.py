import json
import logging
import os
import subprocess

from models.config.config_scanner_snyk import ConfigSnykScanner
from models.creds.creds_scanner import CredsScanner
from models.resources.image import Image
from models.scanner.scanner import Scanner
from models.scanner.scanner_result import ScannerResult


class ScannerSnyk(Scanner):
    """Represents a scanner utilizing Snyk for vulnerability assessment."""

    def __init__(self, credentials: CredsScanner, config: ConfigSnykScanner):
        super().__init__(credentials=credentials, config=config, name=config.name)
        self.token = credentials.password
        self.config: ConfigSnykScanner = config
        self.endpoint = f"{config.hostname}:{config.port}"

    def scan_image(
        self,
        image: Image,
        tag: str,
        registry_username: str,
        registry_password: str,
    ) -> ScannerResult:
        """Scans a container image using Snyk to identify security vulnerabilities.

        This method interacts with the Snyk CLI to perform a security scan on a
        specified container image. The scan results are returned as a
        `ScannerResult`, either indicating successful execution or detailing any
        encountered issues.

        Args:
            image (Image): The container image to be scanned.
            tag (str): The specific tag of the container image.
            registry_username (str): Username for authenticating with the container
                registry.
            registry_password (str): Password for authenticating with the container
                registry.

        Returns:
            ScannerResult: An object representing the scan result, which includes
            scan status and message.

        Raises:
            Exception: General exception if an error occurs during the scan process.
        """
        try:
            env = os.environ.copy()
            env["SNYK_TOKEN"] = self.token  # authenticate
            env["SNYK_API"] = self.endpoint
            result = subprocess.run(
                [
                    "snyk",
                    "container",
                    "test",
                    f"{image.source}:{tag}",
                    f"--username={registry_username}",
                    f"--password={registry_password}",
                    "--sarif",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
                # shell=True,
            )
            if result.returncode in [2, 3]:
                return ScannerResult(
                    ok=False,
                    msg=f"snyk error [{result.returncode}]: {result.stderr.strip()}",
                )

            sarif = json.loads(result.stdout)
            return self.sarif_2_scanner_result(sarif)
        except Exception as e:
            logging.exception(str(2))
            return ScannerResult(ok=False, msg=f"snyk error: {e!s}")
