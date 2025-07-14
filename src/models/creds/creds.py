import base64
import json
import logging
import os
from typing import List, Literal, Union

from models.creds.creds_file import CredsFile
from models.creds.creds_git_repo import CredsGitRepo
from models.creds.creds_helm_registry import CredsHelmRegistry
from models.creds.creds_image_registry import CredsImageRegistry
from models.creds.creds_scanner import CredsScanner

CredType = Literal["helm", "image", "git", "neuvector", "snyk", "cnspec"]
ScannerCredType = Literal["neuvector", "snyk", "cnspec"]


class Creds:
    """
    Handles storage and retrieval of various types of credentials for different services.

    This class is responsible for managing credentials grouped by type, such as image,
    helm, git repositories, and scanner credentials. Each credential is validated to
    prevent duplicates upon initialization. It provides methods to retrieve specific
    credentials by name.

    Attributes:
        helm_creds (List[CredsHelmRegistry]): Stores helm registry credentials.
        image_creds (List[CredsImageRegistry]): Stores image registry credentials.
        git_creds (List[CredsGitRepo]): Stores git repository credentials.
        scanner_creds (List[CredsScanner]): Stores scanner credentials.

    Methods:
        get_git_creds: Retrieves git repository credentials by name.
        get_image_creds: Retrieves image registry credentials by name.
        get_helm_creds: Retrieves helm registry credentials by name.
        get_scanner_creds: Retrieves scanner credentials by type and name.
    """

    def __init__(self, creds_file: CredsFile):
        self.helm_creds: List[CredsHelmRegistry] = []
        self.image_creds: List[CredsImageRegistry] = []
        self.git_creds: List[CredsGitRepo] = []
        self.scanner_creds: List[CredsScanner] = []

        for cred in creds_file.image:
            if self.__is_duplicate(cred):
                logging.warning(f"ignoring duplicate image credential: {cred.name}")
            else:
                self.image_creds.append(cred)

        for cred in creds_file.helm:
            if self.__is_duplicate(cred):
                logging.warning(f"ignoring duplicate helm credential: {cred.name}")
            else:
                self.helm_creds.append(cred)

        for cred in creds_file.git:
            if self.__is_duplicate(cred):
                logging.warning(f"ignoring duplicate git credential: {cred.name}")
            else:
                self.git_creds.append(cred)

        for cred in creds_file.scanners:
            if self.__is_duplicate(cred):
                logging.warning(f"ignoring duplicate scanner credential: {cred.name}")
            else:
                self.scanner_creds.append(cred)

        # write image creds into temporary docker.config file so it can be read by snyk
        for cred in self.image_creds:
            self.write_docker_config(
                registry=cred.name,
                username=cred.username,
                password=cred.password,
                config_path="./tmp/config.json",
            )

    def write_docker_config(self, registry, username, password, config_path="/tmp/config.json"):
        """
        Writes or updates Docker configuration file with registry authentication details.

        This method is used to add or update authentication credentials for a specific
        Docker registry in a Docker configuration file. The configuration file is written
        to the specified location on disk, and the environment is updated to use it.

        Args:
            registry (str): The URL or identifier for the Docker registry.
            username (str): The username for the Docker registry authentication.
            password (str): The password for the Docker registry authentication.
            config_path (str, optional): The file path where the Docker configuration
                file will be stored. Defaults to "/tmp/config.json".

        Raises:
            None

        """
        # Ensure the directory for the config path exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Set the DOCKER_CONFIG environment variable to the directory containing the config file
        os.environ["DOCKER_CONFIG"] = os.path.dirname(config_path)

        config = {}

        # Load existing config if it exists
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {}

        if "auths" not in config:
            config["auths"] = {}

        # Always set or update the credentials
        auth_str = f"{username}:{password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        config["auths"][registry] = {"auth": auth_b64}

        # Write updated config

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"Credentials for '{registry}' written to {config_path}")

    def get_git_creds(self, name) -> CredsImageRegistry:
        """get git creds"""
        return self._get_creds("git", name)

    def get_image_creds(self, name) -> CredsImageRegistry:
        """get image registry creds"""
        return self._get_creds("image", name)

    def get_helm_creds(self, name) -> CredsHelmRegistry:
        """get helm registry creds"""
        return self._get_creds("helm", name)

    def get_scanner_creds(self, scanner_type: ScannerCredType, name: str) -> CredsScanner:
        """get scanner creds"""
        return self._get_creds(scanner_type, name)

    def _get_creds(
        self, cred_type: CredType, name: str
    ) -> Union[CredsHelmRegistry, CredsImageRegistry, CredsGitRepo, CredsScanner]:
        """
        Retrieves the credentials of a specified type and name from the available credential
        lists. If no matching credentials are found, a default credential object is returned.

        Args:
            cred_type (CredType): The type of credential to retrieve. Expected values include
                "helm", "image", "git", "neuvector", "snyk", or "cnspec".
            name (str): The name of the credential to retrieve.

        Returns:
            Union[CredsHelmRegistry, CredsImageRegistry, CredsGitRepo, CredsScanner]: The
            corresponding credential object for the specified type and name. A default object
            is returned if no match is found.

        Raises:
            Exception: If the credential type provided is not recognized.
        """
        match cred_type:
            case "helm":
                return next(
                    (i for i in self.helm_creds if i.name == name),
                    CredsHelmRegistry(name=name, username="", password=""),
                )
            case "image":
                return next(
                    (i for i in self.image_creds if i.name == name),
                    CredsImageRegistry(name=name, username="", password=""),
                )
            case "git":
                return next(
                    (i for i in self.git_creds if i.name == name),
                    CredsGitRepo(name=name, username="", password=""),
                )
            case "neuvector":
                return next(
                    (i for i in self.scanner_creds if i.name == name),
                    CredsScanner(name=name, username="", password="", type="neuvector"),
                )
            case "snyk":
                return next(
                    (i for i in self.scanner_creds if i.name == name),
                    CredsScanner(name=name, username="", password="", type="snyk"),
                )
            case "cnspec":
                return next(
                    (i for i in self.scanner_creds if i.name == name),
                    CredsScanner(name=name, username="", password="", type="cnspec"),
                )
            case _:
                raise ValueError(f"Unknown credential type: {cred_type}")

    def __is_duplicate(self, cred: Union[CredsHelmRegistry, CredsImageRegistry, CredsGitRepo]):
        """
        Determines whether a given credential already exists within its corresponding
        list of credentials.

        Args:
            cred (Union[CredsHelmRegistry, CredsImageRegistry, CredsGitRepo, CredsScanner]):
                The credential object to check for duplication.

        Raises:
            Exception: If cred is of an unrecognized type.

        Returns:
            bool: True if a duplicate credential is found, False otherwise.
        """
        match cred:
            case CredsHelmRegistry():
                return any(existing.name == cred.name for existing in self.helm_creds)
            case CredsImageRegistry():
                return any(existing.name == cred.name for existing in self.image_creds)
            case CredsGitRepo():
                return any(existing.name == cred.name for existing in self.git_creds)
            case CredsScanner():
                return any(existing.name == cred.name for existing in self.scanner_creds)
            case _:
                raise ValueError(f"Unknown credential type: {type(cred)}")
