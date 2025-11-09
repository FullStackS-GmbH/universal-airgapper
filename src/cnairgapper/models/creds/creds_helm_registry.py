from pydantic import BaseModel, Field


class CredsHelmRegistry(BaseModel):
    """Represents credentials for a Helm registry.

    This class is used to store and validate the credentials required for
    authenticating with a Helm registry. It includes fields for the registry
    name, username, and password. The validation ensures that the name follows
    specific constraints, such as having a minimum length of 1 character.
    """

    name: str = Field(..., min_length=1)
    username: str
    password: str
