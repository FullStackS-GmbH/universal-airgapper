from typing import Literal

from pydantic import BaseModel, Field


class ConfigGitRepo(BaseModel):
    """Represents the configuration for a Git repository operation.

    This class is used to define attributes and settings specific to a Git
    repository. It includes source and target repository details, push modes,
    and references (branches, tags, etc.). It is intended to enforce validation
    and constraints on its fields using pydantic `BaseModel`.

    Attributes:
        type (str): Specifies the type of the repository. Must be a non-empty string.
        source_repo (str): Specifies the URL or path of the source repository.
            Must be a non-empty string.
        target_repo (str): Specifies the URL or path of the target repository.
            Must be a non-empty string.
        push_mode (Literal["push", "skip", "force"]): Defines the mode of pushing
            changes (e.g., "push", "skip", or "force").
        refs (list[str]): A list of references (e.g., branches or tags) to operate on.
            The list can include multiple references.
    """

    type: str = Field("git", min_length=1, description="Object of type 'git'")
    source_repo: str = Field(
        ...,
        min_length=1,
        description="URL of the source repository: [https, ssh, git@]",
    )
    target_repo: str = Field(
        ...,
        min_length=1,
        description="URL of the target repository: [https, ssh, git@]",
    )
    push_mode: Literal["push", "skip", "force"] = Field(
        "skip",
        description="skip, try to push or force push if target ref already exists",
    )
    refs: list[str] = Field(
        default_factory=list,
        description="List of references to sync (e.g., branches or tags)",
    )
