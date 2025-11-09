from cnairgapper.models.scanner.scanner_result import ScannerResult


def test_scanner_result_default_initialization():
    result = ScannerResult()
    assert result.ok is True
    assert result.msg == ""
    assert result.issues_critical == 0
    assert result.issues_high == 0
    assert result.issues_medium == 0
    assert result.issues_low == 0
    assert result.issues_unknown == 0


def test_scanner_result_custom_initialization():
    result = ScannerResult(
        ok=False,
        msg="Scan incomplete",
        issues_critical=5,
        issues_high=10,
        issues_medium=15,
        issues_low=20,
        issues_unknown=1,
    )
    assert result.ok is False
    assert result.msg == "Scan incomplete"
    assert result.issues_critical == 5
    assert result.issues_high == 10
    assert result.issues_medium == 15
    assert result.issues_low == 20
    assert result.issues_unknown == 1


def test_scanner_result_partial_initialization():
    result = ScannerResult(issues_high=7, issues_low=3)
    assert result.ok is True
    assert result.msg == ""
    assert result.issues_critical == 0
    assert result.issues_high == 7
    assert result.issues_medium == 0
    assert result.issues_low == 3
    assert result.issues_unknown == 0
