from pydantic import BaseModel, Field


class CredsImageRegistry(BaseModel):
    """Represents credentials for an image registry.

    This class is used to store and manage the information necessary for authenticating
    to an image registry. It includes the registry name, username, and password required
    for accessing the registry.
    """

    name: str = Field(..., min_length=1)
    username: str
    password: str
