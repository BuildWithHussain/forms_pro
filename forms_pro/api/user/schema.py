from frappe.core.doctype.has_role.has_role import HasRole
from pydantic import BaseModel, Field, field_validator


class GetUserTeamsResponseSchema(BaseModel):
    name: str = Field(description="ID of the team")
    team_name: str = Field(description="The name of the team")
    logo: str | None = Field(description="Logo of the team")
    is_current: bool = Field(description="Whether this is the current team")


class GetUserResponseSchema(BaseModel):
    email: str
    first_name: str
    last_name: str | None = None
    full_name: str
    username: str
    desk_theme: str
    roles: list[str]
    has_desk_access: bool

    @field_validator("roles", mode="before")
    @classmethod
    def extract_roles(cls, v: list[HasRole]) -> list[str]:
        if not v:
            return []

        return [role.role for role in v]


class GetUserBasicResponse(BaseModel):
    full_name: str
    user_image: str | None = None
