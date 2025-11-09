import argparse

import configargparse


def create_parser():
    """Creates and configures an `ArgumentParser` for handling command-line arguments.
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

    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
    return parser


def validate_arguments(args: argparse.Namespace, parser: argparse.ArgumentParser) -> bool:
    """Validates the provided command-line arguments to ensure exactly one option is specified
    between mutually exclusive pairs (--credentials-file, --credentials-folder) and
    (--config-file, --config-folder).

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
        parser (argparse.ArgumentParser): The argument parser used for printing help messages.

    Returns:
        bool: True if the arguments are valid, False otherwise.
    """
    # Ensure one (and only one) of --credentials-file or --credentials-folder is provided
    if not bool(args.credentials_file) ^ bool(args.credentials_folder):
        print("You must provide exactly one of --credentials-file or --credentials-folder.")
        parser.print_help()
        return False
    # Ensure one (and only one) of --config-file or --config-folder is provided
    if not bool(args.config_file) ^ bool(args.config_folder):
        print("You must provide exactly one of --config-file or --config-folder.")
        parser.print_help()
        return False
    return True
