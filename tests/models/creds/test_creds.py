from cnairgapper.models.creds.creds import Creds
from cnairgapper.models.creds.creds_file import CredsFile
from cnairgapper.models.creds.creds_git_repo import CredsGitRepo
from cnairgapper.models.creds.creds_helm_registry import CredsHelmRegistry
from cnairgapper.models.creds.creds_image_registry import CredsImageRegistry
from cnairgapper.models.creds.creds_scanner import CredsScanner


def test_creds_initialization_with_empty_creds_file():
    creds_file = CredsFile()  # Empty CredsFile
    creds = Creds(creds_file)

    assert creds.helm_creds == []
    assert creds.image_creds == []
    assert creds.git_creds == []
    assert creds.scanner_creds == []


def test_creds_initialization_with_valid_creds():
    creds_file = CredsFile(
        helm=[CredsHelmRegistry(name="helm1", username="user1", password="pass1")],
        image=[CredsImageRegistry(name="image1", username="user2", password="pass2")],
        git=[CredsGitRepo(name="git1", username="user3", password="pass3")],
        scanners=[CredsScanner(name="scanner1", type="snyk", username="user4", password="pass4")],
    )
    creds = Creds(creds_file)

    assert len(creds.helm_creds) == 1
    assert creds.helm_creds[0].name == "helm1"
    assert creds.helm_creds[0].username == "user1"

    assert len(creds.image_creds) == 1
    assert creds.image_creds[0].name == "image1"
    assert creds.image_creds[0].username == "user2"

    assert len(creds.git_creds) == 1
    assert creds.git_creds[0].name == "git1"
    assert creds.git_creds[0].username == "user3"

    assert len(creds.scanner_creds) == 1
    assert creds.scanner_creds[0].name == "scanner1"
    assert creds.scanner_creds[0].type == "snyk"


def test_creds_duplicate_handling():
    creds_file = CredsFile(
        image=[
            CredsImageRegistry(name="image1", username="user1", password="pass1"),
            CredsImageRegistry(name="image1", username="user1", password="pass1"),
        ]
    )
    creds = Creds(creds_file)

    assert len(creds.image_creds) == 1
    assert creds.image_creds[0].name == "image1"


def test_get_git_creds_existing():
    creds_file = CredsFile(git=[CredsGitRepo(name="git1", username="user1", password="pass1")])
    creds = Creds(creds_file)

    git_creds = creds.get_git_creds("git1")
    assert git_creds.name == "git1"
    assert git_creds.username == "user1"


def test_get_git_creds_non_existing():
    creds_file = CredsFile()
    creds = Creds(creds_file)

    git_creds = creds.get_git_creds("nonexistent")
    assert git_creds.name == "nonexistent"
    assert git_creds.username == ""
    assert git_creds.password == ""


def test_get_scanner_creds_existing():
    creds_file = CredsFile(
        scanners=[CredsScanner(name="scanner1", type="snyk", username="user1", password="pass1")]
    )
    creds = Creds(creds_file)

    scanner_creds = creds.get_scanner_creds("snyk", "scanner1")
    assert scanner_creds.name == "scanner1"
    assert scanner_creds.type == "snyk"
    assert scanner_creds.username == "user1"


def test_get_scanner_creds_non_existing():
    creds_file = CredsFile()
    creds = Creds(creds_file)

    scanner_creds = creds.get_scanner_creds("snyk", "nonexistent")
    assert scanner_creds.name == "nonexistent"
    assert scanner_creds.type == "snyk"
    assert scanner_creds.username == ""
    assert scanner_creds.password == ""
