import pytest

from cli.parser import create_parser


def test_create_parser_missing_required_argument():
    """Test that parser fails when required arguments are missing."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["pull", "--type", "helm"])


def test_create_parser_invalid_subcommand():
    """Test that parser fails when an invalid subcommand is provided."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["invalid-command"])


def test_create_parser_global_debug_flag():
    """Test that the global '--debug' flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(
        [
            "--debug",
            "--credentials-file",
            "/path/to/credentials.yaml",
            "--config-file",
            "/path/to/config.yaml",
        ]
    )
    assert args.debug is True


def test_create_parser_global_credentials_file_argument():
    """Test that the global '--credentials-file' argument is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(
        [
            "--credentials-file",
            "/path/to/credentials.yaml",
            "--config-file",
            "/path/to/config.yaml",
        ]
    )
    assert args.credentials_file == "/path/to/credentials.yaml"


def test_create_parser_global_credentials_folder_argument():
    """Test that the global '--credentials-folder' argument is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(
        [
            "--credentials-folder",
            "/path/to/credentials",
            "--config-file",
            "/path/to/config.yaml",
        ]
    )
    assert args.credentials_folder == "/path/to/credentials"


def test_create_parser_global_config_folder_argument():
    """Test that the global '--config-folder' argument is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(
        [
            "--credentials-folder",
            "/path/to/credentials",
            "--config-folder",
            "/path/to/config",
        ]
    )
    assert args.config_folder == "/path/to/config"
