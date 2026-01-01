import frappe
from frappe.core.doctype.has_role.has_role import HasRole
from pydantic import BaseModel, Field, field_validator

from forms_pro.utils.teams import get_user_teams as get_user_teams_utils


class GetUserTeamsResponseSchema(BaseModel):
    name: str = Field(description="ID of the team")
    team_name: str = Field(description="The name of the team")
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


@frappe.whitelist()
def get_user(user: str) -> GetUserBasicResponse | None:
    """Get basic user data for a given user"""
    data = frappe.db.get_value("User", user, ["full_name", "user_image"], as_dict=True)
    if not data:
        return None
    return GetUserBasicResponse.model_validate(data).model_dump()


@frappe.whitelist()
def get_current_user() -> GetUserResponseSchema:
    """
    Get Current User Data
    """

    user_id = frappe.session.user
    user_doc = frappe.get_doc("User", user_id)
    data = user_doc.as_dict()
    data["roles"] = user_doc.get("roles")
    data["has_desk_access"] = user_doc.has_desk_access()

    return GetUserResponseSchema.model_validate(data).model_dump()


@frappe.whitelist()
def get_user_teams() -> list[GetUserTeamsResponseSchema]:
    """
    Get the list of teams for the current user
    """

    user = frappe.session.user

    if user == "Guest":
        return []

    teams = get_user_teams_utils(user)

    return [GetUserTeamsResponseSchema.model_validate(team).model_dump() for team in teams]
