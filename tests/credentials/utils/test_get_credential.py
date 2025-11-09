from cnairgapper.credentials.utils import get_credential


def test_get_credential_valid_path():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = "user.credentials.username"
    assert get_credential(data, key_path) == "admin"


def test_get_credential_invalid_path():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = "user.name"
    assert get_credential(data, key_path) is None


def test_get_credential_partial_path():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = "user.credentials"
    assert get_credential(data, key_path) == {"username": "admin", "password": "1234"}


def test_get_credential_separator_override():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = "user|credentials|username"
    assert get_credential(data, key_path, separator="|") == "admin"


def test_get_credential_non_dict_intermediate_value():
    data = {"user": {"credentials": ["username", "password"]}}
    key_path = "user.credentials.username"
    assert get_credential(data, key_path) is None


def test_get_credential_empty_key_path():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = ""
    assert get_credential(data, key_path) == data


def test_get_credential_empty_dict():
    data = {}
    key_path = "user.credentials.username"
    assert get_credential(data, key_path) is None


def test_get_credential_none_as_key_path():
    data = {"user": {"credentials": {"username": "admin", "password": "1234"}}}
    key_path = None
    assert get_credential(data, key_path) is data


def test_get_credential_nested_empty_dict():
    data = {"user": {"credentials": {}}}
    key_path = "user.credentials.username"
    assert get_credential(data, key_path) is None
