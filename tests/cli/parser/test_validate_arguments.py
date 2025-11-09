import pytest

from cnairgapper.cli.parser import validate_arguments


class MockArgs:
    def __init__(
        self,
        credentials_file=None,
        credentials_folder=None,
        config_file=None,
        config_folder=None,
    ):
        self.credentials_file = credentials_file
        self.credentials_folder = credentials_folder
        self.config_file = config_file
        self.config_folder = config_folder


class MockParser:
    def __init__(self):
        pass

    def print_help(self):
        """Do nothing."""
        pass


def test_validate_arguments_config_missing():
    args = MockArgs(credentials_file="file.txt")
    parser = MockParser()
    # You must provide exactly one of --config-file or --config-folder.
    assert not validate_arguments(args, parser)


def test_validate_arguments_credentials_missing():
    args = MockArgs(config_file="file.txt")
    parser = MockParser()
    # You must provide exactly one of --credentials-file or --credentials-folder.
    assert not validate_arguments(args, parser)


def test_validate_arguments_credentials_double():
    parser = MockParser()
    args = MockArgs(
        config_file="file.txt", credentials_folder="folder", credentials_file="file.txt"
    )
    # You must provide exactly one of --credentials-file or --credentials-folder.
    assert not validate_arguments(args, parser)


def test_validate_arguments_config_double():
    parser = MockParser()
    args = MockArgs(config_file="file.txt", config_folder="folder", credentials_file="file.txt")
    # You must provide exactly one of --config-file or --config-folder.
    assert not validate_arguments(args, parser)


def test_validate_arguments_fine_1():
    parser = MockParser()
    args = MockArgs(credentials_folder="folder", config_file="config.txt")
    try:
        validate_arguments(args, parser)
    except ValueError:
        pytest.fail("validate_arguments raised ValueError unexpectedly!")


def test_validate_arguments_fine_2():
    parser = MockParser()
    args = MockArgs(credentials_file="file.txt", config_folder="config/folder")
    try:
        validate_arguments(args, parser)
    except ValueError:
        pytest.fail("validate_arguments raised ValueError unexpectedly!")
