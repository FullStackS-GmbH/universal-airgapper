from images.utils import image_to_folder_name


def test_image_to_folder_name_with_tag():
    image_name = "myrepo/myimage:tag"
    expected = "myrepo_myimage_tag"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_digest():
    image_name = "myrepo@sha256:abcdef"
    expected = "myrepo"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_dot_and_digest():
    image_name = "my.repo/image@sha256:def456"
    expected = "my_repo_image"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_special_characters():
    image_name = "my/repo!image:*tag"
    expected = "my_repo_image_tag"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_leading_and_trailing_safe_chars():
    image_name = "_my/repo:image_"
    expected = "my_repo_image"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_alphanumeric_only():
    image_name = "myrepo123"
    expected = "myrepo123"
    result = image_to_folder_name(image_name)
    assert result == expected


def test_image_to_folder_name_with_empty_string():
    image_name = ""
    expected = ""
    result = image_to_folder_name(image_name)
    assert result == expected
