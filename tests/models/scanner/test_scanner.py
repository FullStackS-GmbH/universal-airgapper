from cnairgapper.models.config.config_scanner import ConfigScanner
from cnairgapper.models.creds.creds_scanner import CredsScanner
from cnairgapper.models.scanner.scanner import Scanner


def test_scanner_initialization():
    credentials = CredsScanner(name="scanner_creds", type="basic", username="user", password="pass")
    config = ConfigScanner(name="TestScanner", type="snyk", threshold_critical=5, threshold_high=10)
    scanner = Scanner(name="TestScanner", credentials=credentials, config=config)

    assert scanner.name == "TestScanner"
    assert scanner.credentials == credentials
    assert scanner.config == config
