from models.config.config_image import ConfigImage
from models.resources.image import Image


def test_image_initialization():
    config_image = ConfigImage(
        type="docker",
        source="registry-1.docker.io/library/python:3.13",
        target="registry-2.docker.io/myrepo/python:3.13",
        scan=None,
        tags=["latest", "3.13"],
    )
    image = Image(config_image)

    assert image.source == "registry-1.docker.io/library/python:3.13"
    assert image.target == "registry-2.docker.io/myrepo/python:3.13"
    assert image.scan is None
    assert image.tags == ["latest", "3.13"]


def test_image_source_registry():
    config_image = ConfigImage(
        type="docker",
        source="registry-1.docker.io/library/python:3.13",
        target="registry-2.docker.io/myrepo/python:3.13",
        scan=None,
        tags=["latest", "3.13"],
    )
    image = Image(config_image)

    assert image.source_registry == "registry-1.docker.io"


def test_image_target_registry():
    config_image = ConfigImage(
        type="docker",
        source="registry-1.docker.io/library/python:3.13",
        target="registry-2.docker.io/myrepo/python:3.13",
        scan=None,
        tags=["latest", "3.13"],
    )
    image = Image(config_image)

    assert image.target_registry == "registry-2.docker.io"


def test_image_source_repo_and_name():
    config_image = ConfigImage(
        type="docker",
        source="registry-1.docker.io/library/python:3.13",
        target="registry-2.docker.io/myrepo/python:3.13",
        scan=None,
        tags=["latest", "3.13"],
    )
    image = Image(config_image)

    assert image.source_repo == "library/python"
    assert image.source_name == "3.13"


def test_image_target_repo_and_name():
    config_image = ConfigImage(
        type="docker",
        source="registry-1.docker.io/library/python:3.13",
        target="registry-2.docker.io/myrepo/python:3.13",
        scan=None,
        tags=["latest", "3.13"],
    )
    image = Image(config_image)

    assert image.target_repo == "myrepo/python"
    assert image.target_name == "3.13"


def test_image_default_registry_and_tag():
    config_image = ConfigImage(
        type="docker",
        source="python:3.13",  # No explicit registry or full path
        target="myrepo/python",  # No explicit registry or tag
        scan=None,
        tags=[],
    )
    image = Image(config_image)

    assert image.source_registry == "registry-1.docker.io"
    assert image.source_repo == "library/python"
    assert image.source_name == "3.13"

    assert image.target_registry == "registry-1.docker.io"
    assert image.target_repo == "myrepo/python"
    assert image.target_name == "latest"
