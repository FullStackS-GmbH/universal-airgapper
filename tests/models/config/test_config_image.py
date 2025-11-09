from cnairgapper.models.config.config_image import ConfigImage


def test_config_image_valid_data():
    config = ConfigImage(
        type="docker",
        source="source_path",
        target="target_path",
        scan="full",
        tags=["latest", "stable"],
    )
    assert config.type == "docker"
    assert config.source == "source_path"
    assert config.target == "target_path"
    assert config.scan == "full"
    assert config.tags == ["latest", "stable"]


def test_config_image_optional_scan():
    config = ConfigImage(type="docker", source="source_path", target="target_path", tags=["latest"])
    assert config.scan == ""
    assert config.tags == ["latest"]


def test_config_image_empty_tags():
    config = ConfigImage(type="docker", source="source_path", target="target_path", tags=[])
    assert config.tags == []
