import logging
import os
import sys

from cli.parser import create_parser, validate_arguments
from cli.sync import sync
from config.load_config import load_config_file, load_config_folder
from credentials.load_creds import load_credentials_file, load_credentials_folder
from models.rc import print_rc


def print_version():
    """Prints application version and git commit information."""
    print("=== FullStackS Universal Airgapper ===")
    print(f"app version: {os.environ.get('APP_VERSION', 'unset')}")
    print(f"git commit : {os.environ.get('APP_COMMIT_SHA', 'unset')}")
    print("======================================")


def setup_logging(debug: bool) -> None:
    """
    Configures the logging setup for the application. Adjusts the logging level based
    on whether debugging is enabled or not. When debugging, the logging level is set
    to DEBUG; otherwise, it defaults to INFO. Logging messages will include timestamps,
    module names, log level, and the message content.

    :param debug: A boolean indicating whether to enable debug-level logging.
    :type debug: bool

    :return: This function does not return a value.
    :rtype: None

    :Example:

        >>> setup_logging(True)
        Logs will display all messages at or above the DEBUG level, formatting them
        with timestamps, module names, log level, and message content.

        >>> setup_logging(False)
        Logs will display all messages at or above the INFO level, with the same format.

    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def main():
    """
    Main script entry point.

    This function initiates the main workflow for the application. It handles
    parsing of command-line arguments, setting up logging, loading user
    credentials, and invoking the synchronization process. It also includes
    error handling to log any encountered exceptions and exits the program
    gracefully.

    :raises SystemExit: If an exception occurs during the program execution, this
        function logs the error and exits with status code 1.
    """
    parser = create_parser()
    args = parser.parse_args()
    validate_arguments(args)

    setup_logging(args.debug)
    if args.credentials_file:
        creds_file = load_credentials_file(args.credentials_file)
    else:
        creds_file = load_credentials_folder(args.credentials_folder)

    if args.config_file:
        config_file = load_config_file(args.config_file)
    else:
        config_file = load_config_folder(args.config_folder)

    try:
        rc = sync(config_file=config_file, creds_file=creds_file)
        print_rc(rc)
        if not rc.ok:
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print_version()
    main()
