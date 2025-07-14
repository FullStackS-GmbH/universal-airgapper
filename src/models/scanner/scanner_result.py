from dataclasses import dataclass


@dataclass
class ScannerResult:
    """
    Represents the result of a scanning operation.

    This class is used to encapsulate the results of a scanning operation, including
    the overall status, an optional message, and the count of identified issues
    categorized by severity levels. It provides a structured way to summarize and
    represent the outcomes of a scan.
    """

    ok: bool = True
    msg: str = ""
    issues_critical: int = 0
    issues_high: int = 0
    issues_medium: int = 0
    issues_low: int = 0
    issues_unknown: int = 0
