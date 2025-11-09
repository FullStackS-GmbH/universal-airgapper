from pydantic import BaseModel


class CredsGitRepo(BaseModel):
    """Represents credentials for accessing a Git repository.

    This class is intended to encapsulate the authentication information required
    to interact with a Git repository. It allows specification of a repository name,
    along with optional credentials such as SSH key path, username, and password.
    It can be used in scenarios where programmatic interaction with a Git repository
    is required, such as cloning, pulling, or pushing changes.
    """

    name: str
    ssh_key_path: str | None = None
    username: str | None = None
    password: str | None = None
