from pydantic import BaseModel, Field


class FormSharedWithResponse(BaseModel):
    full_name: str
    user_image: str | None
    email: str = Field(alias="user")
    read: bool
    write: bool
    share: bool
    submit: bool
