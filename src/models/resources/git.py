from urllib.parse import urlparse

from models.config.config_git_repo import ConfigGitRepo


class GitRepo:
    """
    Represents a Git repository and provides utilities for managing repository details.

    This class serves as a representation of a Git repository, initialized with
    configuration details provided by a `ConfigGitRepo` object. It also includes
    methods for retrieving and handling repository-related information, such as
    the hostnames of source and target repositories.

    Attributes:
        type (str): The type of the Git repository.
        source_repo (str): The URL of the source repository.
        target_repo (str): The URL of the target repository.
        push_mode (str): The push mode defined for the repository.
        refs (Any): The references used in the repository.
    """

    def __init__(self, config_repo: ConfigGitRepo):
        self.type = config_repo.type
        self.source_repo = config_repo.source_repo
        self.target_repo = config_repo.target_repo
        self.push_mode = config_repo.push_mode
        self.refs = config_repo.refs

    @property
    def source_repo_host(self) -> str:
        """get source repo hostname"""
        return self._get_repo_hostname(self.source_repo)

    @property
    def target_repo_host(self) -> str:
        """get target repo hostname"""
        return self._get_repo_hostname(self.target_repo)

    @staticmethod
    def _get_repo_hostname(repo_url: str) -> str:
        """
        Retrieves the hostname of a repository from a given repository URL. It handles various URL
        formats such as HTTP, HTTPS, and SSH. In case of an invalid URL, it returns an empty string.
        The function is implemented as a static method for reusable purposes without requiring an
        instance of a class.

        Args:
            repo_url (str): The URL of the repository for which the hostname is to be extracted.

        Returns:
            str: The hostname of the repository if parsing is successful, otherwise an empty string.

        Raises:
            The method does not raise exceptions but handles any exceptions internally by logging
            an error message and returning an empty string.
        """
        try:
            # Parse the URL
            parsed_url = urlparse(repo_url)

            # Handle both SSH and HTTPS/HTTP formats
            if parsed_url.scheme in ["http", "https", "ssh"]:
                return parsed_url.hostname

            # SSH format like git@github.com:repo.git
            if "@" in repo_url and ":" in repo_url:
                return repo_url.split("@")[-1].split(":")[0]
            return ""
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return ""
