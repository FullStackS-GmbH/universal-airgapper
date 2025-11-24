from ..config.config_image import ConfigImage


class Image:
    """Represents an image configuration object by encapsulating information about the image's
    source, target, scan details, and tags.

    This class provides mechanisms to parse image names into meaningful components such as registry,
    repository, and tag. It also enables access to parsed attributes for both the source and target
    images, making it useful for managing image data in containerized environments.

    Attributes:
        source (str): The source image name.
        target (str): The target image name.
        scan (bool): A flag indicating whether scanning is enabled for the image.
        tags (list[str]): A list of tags associated with the image.

    Methods:
        source_registry (str): Retrieves the registry of the source image.
        target_registry (str): Retrieves the registry of the target image.
        source_repo (str): Retrieves the repository of the source image.
        target_repo (str): Retrieves the repository of the target image.
        source_name (str): Retrieves the name and tag of the source image.
        target_name (str): Retrieves the name and tag of the target image.

    Static Methods:
        __parse_image_name (tuple[str, str, str]): Parses a given image name string into its
        components: registry, repository, and tag, defaulting to common values if unspecified.
    """

    def __init__(self, config_image: ConfigImage):
        self.source = config_image.source
        self.target = config_image.target
        self.scan = config_image.scan
        self.tags = config_image.tags
        self.push_mode = config_image.push_mode

    @property
    def source_registry(self):
        """Get source registry."""
        return self.__parse_image_name(self.source)[0]

    @property
    def target_registry(self):
        """Get target registry."""
        return self.__parse_image_name(self.target)[0]

    @property
    def source_repo(self):
        """Get source repo."""
        return self.__parse_image_name(self.source)[1]

    @property
    def target_repo(self):
        """Get source target."""
        return self.__parse_image_name(self.target)[1]

    @property
    def source_name(self):
        """Get source chart name."""
        return self.__parse_image_name(self.source)[2]

    @property
    def target_name(self):
        """Get target chart name."""
        return self.__parse_image_name(self.target)[2]

    @staticmethod
    def __parse_image_name(image_name: str):
        """Parses a given Docker image name into its components: registry, repository, and tag.

        The method separates the Docker image name provided into its constituent
        parts, determining whether the registry is explicitly specified or if
        default values need to be applied. It also identifies the repository and the
        tag, assigning a default tag if none is provided.

        Args:
            image_name (str): The name of the Docker image to be parsed.

        Returns:
            tuple: A tuple containing three strings:
                - registry: The Docker registry from which the image is pulled,
                    defaulting to 'registry-1.docker.io' if not specified.
                - repository: The name of the repository in the registry,
                    defaulting to 'library/{image_name}' if the registry is not explicitly provided.
                - tag: The tag of the image (e.g., version or label),
                    defaulting to 'latest' if not specified.

        Raises:
            None
        """
        default_registry = "registry-1.docker.io"
        default_tag = "latest"

        # Determine the registry and the remaining part of the image name
        if "/" in image_name and "." in image_name.split("/")[0]:
            # registry.some/some/ubuntu:asdf
            # Explicitly provided registry
            registry, rest = image_name.split("/", 1)
        elif "/" in image_name:
            # some/ubuntu:asdf
            registry = default_registry
            rest = image_name
        else:
            # ubuntu:asdf
            # Use default registry and dockerhub default repository
            registry = default_registry
            rest = f"library/{image_name}"

        # Determine the repository and tag
        if ":" in rest:
            repository, tag = rest.rsplit(":", 1)
        else:
            repository = rest
            tag = default_tag

        return registry, repository, tag
