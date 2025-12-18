import frappe
from pydantic import BaseModel, Field

from forms_pro.utils.teams import get_user_teams as get_user_teams_utils


class GetUserTeamsResponseSchema(BaseModel):
    name: str = Field(description="ID of the team")
    team_name: str = Field(description="The name of the team")


class GetUserResponseSchema(BaseModel):
    email: str
    first_name: str
    last_name: str | None = None
    full_name: str
    username: str
    desk_theme: str


@frappe.whitelist()
def get_user() -> GetUserResponseSchema:
    """
    Get Current User Data
    """

    user = frappe.session.user
    data = frappe.get_doc("User", user).as_dict()
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
