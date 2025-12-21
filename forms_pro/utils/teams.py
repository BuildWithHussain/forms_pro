from datetime import datetime
from typing import Any

import frappe
from frappe.defaults import get_user_default, set_user_default
from frappe.query_builder import Case
from pydantic import BaseModel, Field, field_validator


class GetTeamFormsResponseSchema(BaseModel):
    """
    Schema for the response of the get_team_forms function
    """

    name: str = Field(description="ID of the form")
    title: str = Field(description="Title of the form")
    description: str | None = Field(default="", description="Description of the form")
    route: str | None = Field(default="", description="Route of the form")
    is_published: bool = Field(description="Whether the form is published")
    creation: datetime = Field(description="Creation date of the form")
    modified: datetime = Field(description="Modification date of the form")
    linked_team_id: str = Field(description="Team ID of the form")

    @field_validator("creation", "modified", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Convert datetime string to datetime object."""
        if isinstance(v, str):
            return frappe.utils.get_datetime(v)
        if isinstance(v, datetime):
            return v
        raise ValueError(f"Invalid datetime value: {v}")

    @field_validator("is_published", mode="before")
    @classmethod
    def parse_boolean(cls, v: Any) -> bool:
        """Convert 0/1 to boolean."""
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return bool(v)
        if v is None:
            return False
        raise ValueError(f"Invalid boolean value: {v}")

    @field_validator("description", "route", mode="before")
    @classmethod
    def handle_none_strings(cls, v: Any) -> str | None:
        """Handle None values for optional string fields."""
        if v is None:
            return ""
        return v


def get_user_teams(user: str = frappe.session.user):
    """
    Get all Forms Pro teams for a user
    """

    FP_TEAM = frappe.qb.DocType("FP Team")
    FP_TEAM_MEMBER = frappe.qb.DocType("FP Team Member")

    user_default_team = get_user_default("current_team", user)

    query = (
        frappe.qb.from_(FP_TEAM)
        .join(FP_TEAM_MEMBER)
        .on(FP_TEAM.name == FP_TEAM_MEMBER.parent)
        .where(FP_TEAM_MEMBER.user == user)
        .select(
            FP_TEAM.team_name,
            FP_TEAM.name,
            Case().when(FP_TEAM.name == user_default_team, True).else_(False).as_("is_current"),
        )
        .orderby(FP_TEAM.creation)
    )
    teams = query.run(as_dict=True)

    if user_default_team is None and len(teams) > 0:
        teams[0]["is_current"] = True
        set_user_default("current_team", teams[0]["name"])

    return teams or []


def set_current_team(team_name: str, user: str = frappe.session.user):
    set_user_default("current_team", team_name, user)


def get_team_forms(team_id: str) -> list[GetTeamFormsResponseSchema]:
    """
    Get the list of forms for a team

    Args:
        team_id: ID of the team

    Returns:
        list[GetTeamFormsResponseSchema] - List of forms for the team
    """
    forms = frappe.get_all(
        "Form",
        filters={"linked_team_id": team_id},
        fields=[
            "name",
            "title",
            "description",
            "route",
            "is_published",
            "creation",
            "modified",
            "linked_team_id",
        ],
    )

    data = [GetTeamFormsResponseSchema.model_validate(form).model_dump() for form in forms]
    return data
