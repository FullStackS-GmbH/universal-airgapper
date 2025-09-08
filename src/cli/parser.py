import configargparse


def create_parser():
    """
    Creates and configures an `ArgumentParser` for handling command-line arguments.
    This parser is specifically designed for the tool responsible for syncing Docker
    images, Helm charts, and Git repositories. It supports specifying configuration
    and credential files, as well as enabling debug logging. The parser includes
    options for pointing to individual files or folders containing multiple
    configuration formats as required.

    Returns:
        ArgumentParser: Configured `ArgumentParser` instance with specified options
        for handling command-line arguments.
    """
    parser = configargparse.ArgumentParser(
        description="Tool for syncing Docker images, Helm charts, and Git repositories",
        default_config_files=["/etc/airgapper/config.yaml", "~/.airgapper.yaml"],
    )
    # Add credential arguments

    parser.add_argument("--credentials-file", help="Path to a YAML credentials file")
    parser.add_argument(
        "--credentials-folder", help="Path to a folder containing YAML credential files"
    )

    parser.add_argument("--config-file", help="Path to a YAML sync config file")
    parser.add_argument(
        "--config-folder", help="Path to a folder containing YAML sync config files"
    )

    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug logging"
    )
    return parser


def validate_arguments(args):
    """
    Validates the provided command-line arguments to ensure that exactly one of the mutually
    exclusive argument pairs is supplied. This function checks for the presence of either
    credentials or configuration files/folders but not both at the same time.

    Args:
        args (argparse.Namespace): Parsed command-line arguments holding values for
        credentials_file, credentials_folder, config_file, config_folder.

    Raises:
        ValueError: If both or none of the mutually exclusive arguments
        (--credentials-file and --credentials-folder) are provided.
        ValueError: If both or none of the mutually exclusive arguments
        (--config-file and --config-folder) are provided.
    """
    # Ensure one (and only one) of --credentials-file or --credentials-folder is provided
    if not bool(args.credentials_file) ^ bool(args.credentials_folder):
        raise ValueError(
            "You must provide exactly one of --credentials-file or --credentials-folder."
        )
    # Ensure one (and only one) of --config-file or --config-folder is provided
    if not bool(args.config_file) ^ bool(args.config_folder):
        raise ValueError(
            "You must provide exactly one of --config-file or --config-folder."
        )
