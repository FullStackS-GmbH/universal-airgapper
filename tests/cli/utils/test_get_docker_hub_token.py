# import pytest
# import requests
#
# from cli.utils import get_registry_token
#
#
# def test_get_docker_hub_token_for_official_image(requests_mock):
#     requests_mock.get("https://auth.docker.io/token", json={"token": "sample_token"})
#     get_registry_token("ubuntu")
#
#     # Assert that the request was made with correct parameters
#     request = requests_mock.request_history[0]
#     assert (
#         request.url
#         == "https://auth.docker.io/token?service=registry.docker.io&scope=repository%3Alibrary%2Fubuntu%3Apull"  # noqa: E501
#     )
#     assert request.qs == {
#         "service": ["registry.docker.io"],
#         "scope": ["repository:library/ubuntu:pull"],
#     }
#     assert request.headers.get("Authorization") is None
#
#
# def test_get_docker_hub_token_with_credentials(requests_mock):
#     requests_mock.get("https://auth.docker.io/token", json={"token": "private_token"})
#     get_registry_token("private_user/private_repo", "test_user", "test_pass")
#
#     # Assert that the request was made with correct parameters
#     request = requests_mock.request_history[0]
#     assert (
#         request.url
#         == "https://auth.docker.io/token?service=registry.docker.io&scope=repository%3Aprivate_user%2Fprivate_repo%3Apull"  # noqa: E501
#     )
#     assert request.qs == {
#         "service": ["registry.docker.io"],
#         "scope": ["repository:private_user/private_repo:pull"],
#     }
#     auth_header = request.headers.get("Authorization")
#     assert auth_header is not None
#     assert auth_header.startswith("Basic")
#
#
# def test_get_docker_hub_token_raises_for_invalid_response(requests_mock):
#     requests_mock.get("https://auth.docker.io/token", json={})
#     with pytest.raises(KeyError):
#         get_registry_token("invalid/image")
#
#
# def test_get_docker_hub_token_raises_requests_exception(requests_mock):
#     requests_mock.get("https://auth.docker.io/token", exc=requests.exceptions.RequestException)  # noqa: E501
#     with pytest.raises(requests.exceptions.RequestException):
#         get_registry_token("invalid/image")
