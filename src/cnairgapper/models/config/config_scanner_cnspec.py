from typing import Literal

from pydantic import Field

from .config_scanner import ConfigScanner


class ConfigCnspecScanner(ConfigScanner):
    """Represents the configuration for a CNSpec scanner.

    The ConfigCnspecScanner class is a specialization of the ConfigScanner
    class used to manage configurations specific to the CNSpec scanner.
    This class is intended to enable easy manipulation of scanner
    configurations and supports type annotation for better clarity and
    safety.

    Attributes:
        type: A literal string indicating the specific scanner type,
            which is "cnspec".
    """

    type: Literal["cnspec"]
    incognito: bool = Field(
        default=False,
        description="Whether to use incognito mode for the scanner. Defaults to False.",
    )
