from typing import Literal

from pydantic import Field

from models.config.config_scanner import ConfigScanner


class ConfigNeuvectorScanner(ConfigScanner):
    """
    Represents a configuration for the NeuVector scanner.

    This class inherits from ConfigScanner and is designed to store configuration
    parameters specifically for the NeuVector vulnerability scanner. It defines
    attributes required for establishing a connection to the scanner, such as the
    hostname, port, and whether TLS verification should be performed.
    """

    type: Literal["neuvector"]
    hostname: str = Field(..., min_length=1, description="Hostname of the NeuVector scanner.")
    port: int = Field(..., ge=1, le=65535, description="Port number of the NeuVector scanner.")
    verify_tls: bool = Field(
        default=True,
        description="Whether to verify TLS certificates when connecting to the scanner.",
    )
