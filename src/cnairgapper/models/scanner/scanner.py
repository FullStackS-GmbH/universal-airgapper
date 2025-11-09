from ..config.config_scanner import ConfigScanner
from ..creds.creds_scanner import CredsScanner
from ..resources.image import Image
from .scanner_result import ScannerResult


class Scanner:
    """Represents a scanner for analyzing container images.

    The Scanner class provides functionality to scan container images in order
    to perform analysis. It integrates with credentials and configuration objects
    to facilitate the scanning process, which can include security analysis,
    content validation, or other image-related inspection tasks.
    """

    def __init__(self, name: str, credentials: CredsScanner, config: ConfigScanner):
        self.name = name
        self.credentials = credentials
        self.config = config

    def scan_image(
        self, image: Image, tag: str, registry_username: str, registry_password: str
    ) -> ScannerResult:
        """Interface."""

    def _result_is_okay(self, result: ScannerResult) -> (bool, str):
        """Determines if a given scanner result meets configured thresholds.

        This method checks the low, medium, high, and critical issue counts in the scanner result
        against the respective configured thresholds. If any of the thresholds are exceeded, it
        returns a tuple indicating failure along with an appropriate message. If all thresholds
        are met, it returns a success status with a "result fine" message.

        Args:
            result (ScannerResult): The scanner result containing issue counts to be
                validated against configured thresholds.

        Returns:
            tuple[bool, str]: A tuple where the first element is a boolean indicating whether the
                              result is within acceptable thresholds (True is acceptable),
                              and the second element is a string that contains a message about the
                              result status.

        Raises:
            None
        """
        if self.config.threshold_low != -1:
            if result.issues_low > self.config.threshold_low:
                return (
                    False,
                    f"low threshold exceeded: {result.issues_low}/{self.config.threshold_low}",
                )
        if self.config.threshold_medium != -1:
            if result.issues_medium > self.config.threshold_medium:
                return (
                    False,
                    f"medium threshold exceeded: {result.issues_medium}/{self.config.threshold_medium}",  # noqa: E501
                )

        if self.config.threshold_high != -1:
            if result.issues_high > self.config.threshold_high:
                return (
                    False,
                    f"high threshold exceeded: {result.issues_high}/{self.config.threshold_high}",
                )

        if self.config.threshold_critical != -1:
            if result.issues_critical > self.config.threshold_critical:
                return (
                    False,
                    f"critical threshold exceeded: {result.issues_critical}/{self.config.threshold_critical}",  # noqa: E501
                )
        return (True, "result fine")

    def sarif_2_scanner_result(self, report: dict) -> ScannerResult:
        """Converts a SARIF formatted report into a ScannerResult object.

        This method takes a report in SARIF format and processes it to count
        the number of issues at different severity levels: critical, medium,
        low, and unknown. The method then evaluates if the resulting ScannerResult
        indicates that the processing is successful or contains any errors.

        Args:
            report (dict): A dictionary representing the input SARIF report,
                           formatted according to the SARIF standard version 2.1.0.

        Returns:
            ScannerResult: An instance of ScannerResult containing the processed data
                           including the count of issues by severity (critical, medium,
                           low, unknown) and the final status (okay or not okay) along
                           with the associated message.
        """
        # https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html#_Toc141790898
        result = ScannerResult()
        # results.level: [warning, error, note, none]
        # error -> critical
        # warning -> medium
        # note -> low
        for vuln in report["runs"][0]["results"]:
            match vuln["level"]:
                case "error":
                    result.issues_critical += 1
                case "warning":
                    result.issues_medium += 1
                case "note":
                    result.issues_low += 1
                case _:
                    result.issues_unknown += 1
        (result.okay, result.msg) = self._result_is_okay(result=result)
        return result

    def cnspec_2_scanner_result(self, report: dict) -> ScannerResult:
        """Converts a cnspec JSON formatted report to a ScannerResult object.

        This function processes a cnspec JSON formatted report and converts its
        data into a `ScannerResult` object. It classifies vulnerabilities based
        on their severity levels (e.g., "error", "warning", "note") and updates
        the respective attributes of the `ScannerResult` object. It also checks
        and updates whether the result is considered okay and attaches a message
        accordingly.

        Args:
            report (dict): The dictionary containing the cnspec JSON formatted
                vulnerability report. It must include the 'runs' key with a list
                containing elements that have 'results' and 'level' keys.

        Returns:
            ScannerResult: An object representing the processed vulnerability
                report, including counts of critical, medium, low, and unknown
                severity issues.

        Raises:
            KeyError: If the required keys (`runs`, `results`, `level`) are missing
                in the provided report.
        """
        # must be adapted to cnspec json format
        # to be discussed with mondoo
        result = ScannerResult()

        result.issues_critical = report["stats"]["advisories"]["critical"]
        result.issues_high = report["stats"]["advisories"]["high"]
        result.issues_medium = report["stats"]["advisories"]["medium"]
        result.issues_low = report["stats"]["advisories"]["low"]
        result.issues_unknown = report["stats"]["advisories"]["unknown"]

        (result.okay, result.msg) = self._result_is_okay(result=result)
        return result

    def neuvector_2_scanner_result(self, report: dict) -> ScannerResult:
        """Converts a NeuVector vulnerability report into a standardized ScannerResult
        object. This function processes the NeuVector report to calculate the number
        of vulnerabilities categorized by severity levels (Critical, High, Medium,
        Low, and Unknown).

        Args:
            report (dict): A dictionary containing the NeuVector vulnerability report.
                           It must include a "vulnerabilities" key with a list of
                           vulnerability records.

        Returns:
            ScannerResult: A standardized result object summarizing the count of
                           vulnerabilities by severity and the overall status of the
                           scanning result.
        """
        result = ScannerResult()
        for vuln in report["vulnerabilities"]:
            match vuln["severity"]:
                case "Critical":
                    result.issues_critical += 1
                case "High":
                    result.issues_high += 1
                case "Medium":
                    result.issues_medium += 1
                case "Low":
                    result.issues_low += 1
                case _:
                    result.issues_unknown += 1
        (result.ok, result.msg) = self._result_is_okay(result=result)
        return result
