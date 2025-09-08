from typing import Literal, Optional

from pydantic import BaseModel, Field


class ConfigImage(BaseModel):
    """
    Holds configuration details for an image and its related operations.

    This class is designed to represent the configuration data required for
    performing operations on a specific image, such as providing source and target
    details, specifying a scanner for the image, and specifying any associated tags.

    Attributes:
        type: Object of type 'image'.
        source: Source image fully qualified name, without the tag. For example:
            `registry.lab.cloudstacks.eu/base-images/maven-graal`.
        target: Target image fully qualified name, without the tag.
        scan: Optional name of the scanner to use for this image.
        tags: List of tags to synchronize for this image.
    """

    type: str = Field("image", min_length=1, description="Object of type 'image'")
    source: str = Field(
        ...,
        min_length=1,
        description="""
            Source image fully qualified name, without tag.
            eg.: registry.lab.cloudstacks.eu/base-images/maven-graal
        """,
    )
    target: str = Field(
        ..., min_length=1, description="Target image fully qualified name, without tag."
    )
    push_mode: Literal["skip", "force"] = Field(
        "force",
        description="force, try to force push if target ref already exists or skip",
    )
    scan: Optional[str] = Field(
        "", description=".name of the scanner to use for this image"
    )
    tags: list[str] = Field(
        default_factory=list, description="List of tags to sync for this image."
    )
