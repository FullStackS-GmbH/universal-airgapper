from pydantic import BaseModel, Field

from .creds_git_repo import CredsGitRepo
from .creds_helm_registry import CredsHelmRegistry
from .creds_image_registry import CredsImageRegistry
from .creds_scanner import CredsScanner


class CredsFile(BaseModel):
    """Represents a data structure to manage and store different types of credentials.

    The CredsFile class provides a cohesive structure for organizing and accessing
    credentials related to scanners, image registries, Helm repositories, and Git
    repositories. It is designed to simplify the management of such credentials by
    categorizing them into specific lists. This class is particularly useful in
    scenarios where multiple credential sources need to be organized and handled
    systematically.

    Attributes:
        scanners (Optional[List[CredsScanner]]): A list of scanner credentials.
        image (Optional[List[CredsImageRegistry]]): A list of image registry credentials.
        helm (Optional[List[CredsHelmRegistry]]): A list of Helm repository credentials.
        git (Optional[List[CredsGitRepo]]): A list of Git repository credentials.
    """

    scanners: list[CredsScanner] | None = Field(default_factory=list)
    image: list[CredsImageRegistry] | None = Field(default_factory=list)
    helm: list[CredsHelmRegistry] | None = Field(default_factory=list)
    git: list[CredsGitRepo] | None = Field(default_factory=list)
