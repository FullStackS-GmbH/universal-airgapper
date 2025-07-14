from typing import Literal

from pydantic import Field

from models.config.config_scanner import ConfigScanner


class ConfigSnykScanner(ConfigScanner):
    """
    Represents configuration settings for a Snyk Endpoint scanner.

    This class extends the base ConfigScanner class to define specific
    configuration parameters necessary for interacting with the Snyk Endpoint
    scanner. It provides options to configure the hostname, port, and TLS
    verification behavior for secure communication with the endpoint.

    Attributes:
        hostname: Hostname of the Snyk Endpoint scanner that this class will
            connect to. Must be a non-empty string.
        port: Port number on which the Snyk Endpoint scanner is running.
            Defaults to 443. Must be between 1 and 65535 inclusive.
        verify_tls: A boolean indicating whether to verify TLS certificates when
            connecting to the Snyk Endpoint. Defaults to True for secure
            connections.
    """

    type: Literal["snyk"]
    hostname: str = Field("api.snyk.io", description="Hostname of the Snyk Endpoint scanner.")
    port: int = Field(443, ge=1, lt=65536, description="Port number of the Snyk Endpoint scanner.")
    verify_tls: bool = Field(
        default=True,
        description="Whether to verify TLS certificates when connecting to the Snyk Endpoint.",
    )
