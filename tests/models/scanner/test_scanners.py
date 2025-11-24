from cnairgapper.models.config.config_scanner_neuvector import ConfigNeuvectorScanner
from cnairgapper.models.creds.creds_scanner import CredsScanner
from cnairgapper.models.scanner.scanner import Scanner
from cnairgapper.models.scanner.scanner_neuvector import ScannerNeuVector
from cnairgapper.models.scanner.scanners import Scanners


def test_scanners_initialization_with_empty_list():
    scanners = Scanners(scanners=[])
    assert scanners.scanners == []


def test_add_scanner_with_neuvector_config():
    scanners = Scanners(scanners=[])
    creds = CredsScanner(name="scanner1", type="neuVector", username="user", password="pass")
    config = ConfigNeuvectorScanner(
        type="neuvector",
        name="neuVectorScanner",
        hostname="localhost",
        port=8443,
        verify_tls=True,
    )
    scanners.add_scanner(scanner=config, creds=creds)
    assert len(scanners.scanners) == 1
    assert isinstance(scanners.scanners[0], ScannerNeuVector)
    assert scanners.scanners[0].credentials.username == "user"
    assert scanners.scanners[0].config.hostname == "localhost"


def test_get_scanner_returns_correct_scanner():
    creds = CredsScanner(name="scanner1", type="neuVector", username="user", password="pass")
    config = ConfigNeuvectorScanner(
        type="neuvector",
        name="neuVectorScanner",
        hostname="localhost",
        port=8443,
        verify_tls=True,
    )

    scanner = ScannerNeuVector(credentials=creds, config=config)

    scanners = Scanners(scanners=[scanner])
    fetched_scanner = scanners.get_scanner("neuVectorScanner")

    assert fetched_scanner is not None
    assert fetched_scanner.name == "neuVectorScanner"
    assert isinstance(fetched_scanner, Scanner)


def test_get_scanner_returns_none_on_invalid_name():
    creds = CredsScanner(name="scanner1", type="neuVector", username="user", password="pass")
    config = ConfigNeuvectorScanner(
        type="neuvector",
        name="neuVectorScanner",
        hostname="localhost",
        port=8443,
        verify_tls=True,
    )

    scanner = ScannerNeuVector(credentials=creds, config=config)

    scanners = Scanners(scanners=[scanner])
    fetched_scanner = scanners.get_scanner("invalid_name")

    assert fetched_scanner is None
