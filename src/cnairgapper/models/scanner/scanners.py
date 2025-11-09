import logging

from ..config.config_scanner_cnspec import ConfigCnspecScanner
from ..config.config_scanner_neuvector import ConfigNeuvectorScanner
from ..config.config_scanner_snyk import ConfigSnykScanner
from ..creds.creds_scanner import CredsScanner
from .scanner import Scanner
from .scanner_cnspec import ScannerCnspec
from .scanner_neuvector import ScannerNeuVector
from .scanner_snyk import ScannerSnyk


class Scanners:
    """Represents a collection of scanners and provides utilities to manage them.

    The Scanners class encapsulates a list of scanner instances, allowing for the
    addition and retrieval of scanners. It supports the integration of specific
    scanner types configured with credentials. This class can be used in contexts
    where multiple scanners need to be managed effectively as a group.
    """

    def __init__(self, scanners: list[Scanner]):
        self.scanners = scanners

    # TODO: check for duplicate scanners

    def add_scanner(
        self,
        scanner: ConfigNeuvectorScanner | ConfigSnykScanner | ConfigCnspecScanner,
        creds: CredsScanner,
    ):
        """Adds a new scanner to the list of scanners. The method determines the type
        of the scanner based on pattern matching and appends a suitable instance
        to the `scanners` list. This method primarily supports scanners of type
        `ConfigNeuvectorScanner`.

        Args:
            scanner (Union[ConfigNeuvectorScanner]): The configuration object of the scanner.
            creds (CredsScanner): Credentials required to authenticate the scanner.

        Raises:
            ValueError: If the provided scanner type is not supported.
        """
        match scanner:
            case ConfigNeuvectorScanner():
                self.scanners.append(ScannerNeuVector(credentials=creds, config=scanner))
            case ConfigSnykScanner():
                self.scanners.append(ScannerSnyk(credentials=creds, config=scanner))
            case ConfigCnspecScanner():
                self.scanners.append(ScannerCnspec(credentials=creds, config=scanner))

    def get_scanner(self, name: str):
        """Gets a scanner object with the specified name from the list of scanners.

        This method searches through the list of scanner objects and retrieves the
        scanner whose name matches the specified name. If no scanner is found with
        the provided name, an error is logged, and None is returned. Scanner names
        are assumed to be unique within the collection.

        Args:
            name (str): The name of the scanner to retrieve.

        Returns:
            Optional[Scanner]: The scanner object if found, otherwise None.
        """
        if not name:
            return None
        s = next((i for i in self.scanners if i.name == name), None)
        if not s:
            logging.error(f"Scanner '{name}' not found.")
        return s
