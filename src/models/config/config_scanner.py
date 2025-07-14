from typing import Literal

from pydantic import BaseModel, Field


class ConfigScanner(BaseModel):
    """
    Represents a configuration model for a security scanner.

    This class defines the configuration attributes for different types of security
    scanning tools. It allows specifying the scanner's name, type, and customizable
    thresholds for varying severity levels of vulnerabilities. The thresholds help
    determine acceptable limits for critical, high, medium, and low-severity issues
    in the scanning process.

    Attributes:
        name (str): The name of the scanner. Must be at least 1 character long.
        type (Literal["neuvector", "snyk", "cnspec"]): The type of scanner being
            used. Valid options are "neuvector", "snyk", or "cnspec".
        threshold_critical (int): The maximum acceptable number of critical
            severity issues. Defaults to 0.
        threshold_high (int): The maximum acceptable number of high severity
            issues. Defaults to 0.
        threshold_medium (int): The maximum acceptable number of medium severity
            issues. Defaults to 0.
        threshold_low (int): The maximum acceptable number of low severity issues.
            Defaults to 0.
    """

    name: str = Field(..., min_length=1, description="Name aka identifier of the scanner")
    type: Literal["neuvector", "snyk", "cnspec"] = Field(..., description="Type of scanner")
    threshold_critical: int = Field(
        0, ge=-1, lt=999, description="Max number of critical vulnerability issues"
    )
    threshold_high: int = Field(
        0, ge=-1, lt=999, description="Max number of high vulnerability issues"
    )
    threshold_medium: int = Field(
        0, ge=-1, lt=999, description="Max number of medium vulnerability issues"
    )
    threshold_low: int = Field(
        0, ge=-1, lt=999, description="Max number of low vulnerability issues"
    )
