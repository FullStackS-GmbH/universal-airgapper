# from config.sync_config import _validate_sync_config
#
#
# def test_validate_sync_config_valid_docker_config():
#     valid_config = {
#         "resources": [
#             {
#                 "type": "docker",
#                 "source": "my_source",
#                 "destination": "my_destination",
#                 "tags": ["v1.0.0", "v1.0.1"],
#             }
#         ]
#     }
#     assert _validate_sync_config(valid_config) is True
#
#
# def test_validate_sync_config_valid_helm_config():
#     valid_config = {
#         "resources": [
#             {
#                 "type": "helm",
#                 "source_registry": "my_registry",
#                 "source_chart": "my_chart",
#                 "destination_registry": "my_destination_registry",
#                 "destination_repo": "https://example.com/repo",
#                 "versions": ["1.0.0", "1.2.3"],
#             }
#         ]
#     }
#     assert _validate_sync_config(valid_config) is True
#
#
# def test_validate_sync_config_valid_git_config():
#     valid_config = {
#         "resources": [
#             {
#                 "type": "git",
#                 "source_repo": "https://example.com/source.git",
#                 "destination_repo": "https://example.com/destination.git",
#                 "refs": ["main", "feature-branch"],
#             }
#         ]
#     }
#     assert _validate_sync_config(valid_config) is True
#
#
# def test_validate_sync_config_invalid_type():
#     invalid_config = {
#         "resources": [
#             {"type": "invalid_type", "source": "my_source", "destination": "my_destination"}  # noqa: E501
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_missing_required_field_docker():
#     invalid_config = {
#         "resources": [
#             {
#                 "type": "docker",
#                 "source": "my_source",
#                 "destination": "my_destination"
#                 # Missing "tags"
#             }
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_missing_required_field_helm():
#     invalid_config = {
#         "resources": [
#             {
#                 "type": "helm",
#                 "source_registry": "my_registry",
#                 "destination_registry": "my_destination_registry",
#                 "destination_repo": "https://example.com/repo",
#                 "versions": ["1.0.0", "1.2.3"]
#                 # Missing "source_chart"
#             }
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_missing_required_field_git():
#     invalid_config = {
#         "resources": [
#             {
#                 "type": "git",
#                 "source_repo": "https://example.com/source.git",
#                 "refs": ["main", "feature-branch"]
#                 # Missing "destination_repo"
#             }
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_invalid_extra_field():
#     invalid_config = {
#         "resources": [
#             {
#                 "type": "docker",
#                 "source": "my_source",
#                 "destination": "my_destination",
#                 "tags": ["v1.0.0", "v1.0.1"],
#                 "extra_field": "not_allowed",
#             }
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_empty_resources():
#     valid_config = {"resources": []}
#     assert _validate_sync_config(valid_config) is True
#
#
# def test_validate_sync_config_missing_resources():
#     valid_config = {}
#     assert _validate_sync_config(valid_config) is False
#
#
# def test_validate_sync_config_invalid_chart_repo():
#     invalid_config = {
#         "resources": [
#             {
#                 "type": "helm",
#                 "source_registry": "https://source.helm.com",
#                 "source_repo": "your/repo",
#                 "destination_registry": "target.helm.com",
#                 "destination_repo": "my/repo",
#                 "versions": ["1.0.0", "1.2.3"],
#             }
#         ]
#     }
#     assert _validate_sync_config(invalid_config) is False
#
#
# def test_validate_sync_config_with_neuvector():
#     invalid_config = {
#         "resources": [],
#         "neuvector": {
#             "hostname": "hugo",
#             "port": 1234,
#             "threshold_critical": 9,
#             "threshold_high": 9,
#             "threshold_medium": 9,
#             "threshold_low": 9,
#             "verify_tls": False,
#         },
#     }
#     assert _validate_sync_config(invalid_config) is True
