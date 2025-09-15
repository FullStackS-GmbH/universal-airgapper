import pytest

from cli.parser import validate_arguments


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


def test_validate_arguments_config_missing():
    args = MockArgs(credentials_file="file.txt")
    with pytest.raises(
        ValueError,
        match="You must provide exactly one of --config-file or --config-folder.",
    ):
        validate_arguments(args)


def test_validate_arguments_credentials_missing():
    args = MockArgs(config_file="file.txt")
    with pytest.raises(
        ValueError,
        match="You must provide exactly one of --credentials-file or --credentials-folder.",
    ):
        validate_arguments(args)


def test_validate_arguments_credentials_double():
    args = MockArgs(
        config_file="file.txt", credentials_folder="folder", credentials_file="file.txt"
    )
    with pytest.raises(
        ValueError,
        match="You must provide exactly one of --credentials-file or --credentials-folder.",
    ):
        validate_arguments(args)


def test_validate_arguments_config_double():
    args = MockArgs(config_file="file.txt", config_folder="folder", credentials_file="file.txt")
    with pytest.raises(
        ValueError,
        match="You must provide exactly one of --config-file or --config-folder.",
    ):
        validate_arguments(args)


def test_validate_arguments_fine_1():
    args = MockArgs(credentials_folder="folder", config_file="config.txt")
    try:
        validate_arguments(args)
    except ValueError:
        pytest.fail("validate_arguments raised ValueError unexpectedly!")


def test_validate_arguments_fine_2():
    args = MockArgs(credentials_file="file.txt", config_folder="config/folder")
    try:
        validate_arguments(args)
    except ValueError:
        pytest.fail("validate_arguments raised ValueError unexpectedly!")
