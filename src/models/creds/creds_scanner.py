from pydantic import BaseModel, Field


class CredsScanner(BaseModel):
    """
    Represents a credential scanner model.

    This class is used to store the details of credentials such as name, type,
    username, and password. Each field has specific validation requirements
    and constraints enforced by the `Field` definitions. It is part of a larger
    system to manage and work with credentials in various contexts.
    """

    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    username: str
    password: str
