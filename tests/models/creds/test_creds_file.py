from cnairgapper.models.creds.creds_file import CredsFile
from cnairgapper.models.creds.creds_git_repo import CredsGitRepo
from cnairgapper.models.creds.creds_helm_registry import CredsHelmRegistry
from cnairgapper.models.creds.creds_image_registry import CredsImageRegistry
from cnairgapper.models.creds.creds_scanner import CredsScanner


def test_creds_file_initialization_with_defaults():
    creds_file = CredsFile()
    assert creds_file.scanners == []
    assert creds_file.image == []
    assert creds_file.helm == []
    assert creds_file.git == []


def test_creds_file_with_scanners():
    scanner = CredsScanner(name="Scanner1", type="TypeA", username="user", password="pass")
    creds_file = CredsFile(scanners=[scanner])
    assert len(creds_file.scanners) == 1
    assert creds_file.scanners[0].name == "Scanner1"
    assert creds_file.scanners[0].type == "TypeA"
    assert creds_file.scanners[0].username == "user"
    assert creds_file.scanners[0].password == "pass"


def test_creds_file_with_image_registries():
    image_registry = CredsImageRegistry(
        name="Registry1", username="image_user", password="image_pass"
    )
    creds_file = CredsFile(image=[image_registry])
    assert len(creds_file.image) == 1
    assert creds_file.image[0].name == "Registry1"
    assert creds_file.image[0].username == "image_user"
    assert creds_file.image[0].password == "image_pass"


def test_creds_file_with_helm_registries():
    helm_registry = CredsHelmRegistry(name="HelmRepo1", username="helm_user", password="helm_pass")
    creds_file = CredsFile(helm=[helm_registry])
    assert len(creds_file.helm) == 1
    assert creds_file.helm[0].name == "HelmRepo1"
    assert creds_file.helm[0].username == "helm_user"
    assert creds_file.helm[0].password == "helm_pass"


def test_creds_file_with_git_repos():
    git_repo = CredsGitRepo(
        name="Repo1",
        ssh_key_path="/path/to/key",
        username="git_user",
        password="git_pass",
    )
    creds_file = CredsFile(git=[git_repo])
    assert len(creds_file.git) == 1
    assert creds_file.git[0].name == "Repo1"
    assert creds_file.git[0].ssh_key_path == "/path/to/key"
    assert creds_file.git[0].username == "git_user"
    assert creds_file.git[0].password == "git_pass"
