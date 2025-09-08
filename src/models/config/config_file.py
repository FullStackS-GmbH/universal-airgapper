from pydantic import BaseModel, Field

from models.config.config_git_repo import ConfigGitRepo
from models.config.config_helm_chart import ConfigHelmChart
from models.config.config_image import ConfigImage
from models.config.config_scanner_cnspec import ConfigCnspecScanner
from models.config.config_scanner_neuvector import ConfigNeuvectorScanner
from models.config.config_scanner_snyk import ConfigSnykScanner


class ConfigFile(BaseModel):
    """Represents a configuration file used for managing and organizing different
    resources and scanners within a system.

    This class is a data model that defines the structure of the configuration
    file. It includes optional lists of resources and scanners, each modeled by
    dedicated configurations. Resources may include entities such as Git
    repositories, container images, Helm charts, and others. Scanners are tools
    designed to analyze or inspect these resources. The configuration file can
    be easily extended by enabling future integrations, marked by TODOs.

    Attributes:
        resources: List of resource configurations, which may include Git
            repositories, images, Helm charts, etc. An empty list is assigned
            by default if no resources are provided.
        scanners: List of scanner configurations, specifically instances of
            Neuvector scanners. An empty list is assigned by default if no
            scanners are provided.
    """

    resources: list[ConfigGitRepo | ConfigImage | ConfigHelmChart] | None = Field(
        default_factory=list,
        description="List of resources to sync: Git Repo, Image, Helm Chart",
    )
    scanners: list[ConfigNeuvectorScanner | ConfigSnykScanner | ConfigCnspecScanner] | None = Field(
        default_factory=list,
        description="List of available scanners: Neuvector, Snyk, Cnspec,..",
    )
