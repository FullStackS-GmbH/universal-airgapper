import logging

from ..resources.git import GitRepo
from ..resources.image import Image
from .config_git_repo import ConfigGitRepo
from .config_helm_chart import ConfigHelmChart
from .config_image import ConfigImage


class SyncResources:
    """Class to manage synchronization of different resource types.

    This class is designed to handle the synchronization of various resource
    types, including Helm charts, container images, and Git repositories.
    It provides methods to add these resources, while preventing duplicates
    using overlap checks based on predefined rules.

    Attributes:
        images (List[Image]): A list of Image objects representing the container
            images to be synchronized.
        charts (List[ConfigHelmChart]): A list of ConfigHelmChart objects
            representing the Helm charts to be synchronized.
        repos (List[GitRepo]): A list of GitRepo objects representing the
            Git repositories to be synchronized.

    Args:
        resources (List[Union[ConfigHelmChart, ConfigImage, ConfigGitRepo]]):
            A list of resources of varying types to be synchronized.

    Raises:
        Exception: Raised in the event of an unrecognized resource type.
    """

    def __init__(self, resources: list[ConfigHelmChart | ConfigImage | ConfigGitRepo]):
        self.images: list[Image] = []
        self.charts: list[ConfigHelmChart] = []
        self.repos: list[GitRepo] = []

        for res in resources:
            match res:
                case ConfigHelmChart():
                    self.add_helm(res)
                case ConfigImage():
                    self.add_image(res)
                case ConfigGitRepo():
                    self.add_git(res)
                case _:
                    raise ValueError(f"Unknown resource type: {type(res)}")

    def add_helm(self, chart: ConfigHelmChart):
        """Adds a new helm chart configuration."""
        if self.__has_overlap(chart):
            logging.warning(f"duplicate helm chart? {chart.source_registry}/{chart.source_chart}")
        else:
            self.charts.append(chart)

    def add_image(self, image: ConfigImage):
        """Adds a new image configuration."""
        if self.__has_overlap(image):
            logging.warning(f"duplicate image? {image.source}")
        else:
            self.images.append(Image(image))

    def add_git(self, repo: ConfigGitRepo):
        """Adds a new Git repository configuration."""
        if self.__has_overlap(repo):
            logging.warning(f"duplicate repo? {repo.source_repo}")
        else:
            self.repos.append(GitRepo(repo))

    def __has_overlap(self, resource: ConfigHelmChart | ConfigImage | ConfigGitRepo):
        """Determines if there is an overlap between the given resource and the existing
        resources in the current object. Compares the resource's source properties
        with the sources of already stored resources of the same type.

        Args:
            resource (Union[ConfigHelmChart, ConfigImage, ConfigGitRepo]): The resource
                for which overlap is being checked. It can be one of ConfigHelmChart,
                ConfigImage, or ConfigGitRepo.

        Returns:
            bool: True if there is an overlap between the given resource and existing
                resources of the same type, False otherwise.

        Raises:
            Exception: If the provided resource type is not recognized.
        """
        match resource:
            case ConfigHelmChart():
                return any(
                    existing.source_chart == resource.source_chart
                    and existing.source_registry == resource.source_registry
                    for existing in self.charts
                )
            case ConfigImage():
                return any(existing.source == resource.source for existing in self.images)
            case ConfigGitRepo():
                return any(existing.source_repo == resource.source_repo for existing in self.repos)
            case _:
                raise ValueError(f"Unknown resource type: {type(resource)}")
