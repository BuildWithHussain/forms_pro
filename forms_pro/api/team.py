import frappe

from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam, GetTeamMembersResponse
from forms_pro.utils.teams import GetTeamFormsResponseSchema, set_current_team
from forms_pro.utils.teams import get_team_forms as get_team_forms_utils


@frappe.whitelist()
def get_team_forms(team_id: str) -> list[GetTeamFormsResponseSchema]:
    """
    Get the list of forms for the current team

    Args:
        team_id: ID of the team

    Returns:
        list[GetTeamFormsResponseSchema] - List of forms for the team
    """
    forms = get_team_forms_utils(team_id=team_id)
    return forms


@frappe.whitelist()
def get_team_members(team_id: str) -> list[GetTeamMembersResponse]:
    """

    Get the list of team members in a FP Team.
    This endpoint checks if the session user has the permission to read this FP Team DocType

    """
    frappe.has_permission(
        doctype="FP Team",
        ptype="read",
        doc=team_id,
        user=frappe.session.user,
        throw=True,
    )

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    members = team.team_members

    return members


@frappe.whitelist(methods=["POST"])
def create_team(team_name: str) -> FPTeam:
    """
    Create a new team

    Args:
        team_name: Name of the team

    Returns:
        FPTeam - The created team
    """

    team: FPTeam = frappe.new_doc("FP Team")
    team.team_name = team_name
    team.insert()
    return team


@frappe.whitelist(methods=["POST"])
def switch_team(team_id: str) -> None:
    """
    Switch to a new team
    """

    if not frappe.has_permission(
        doctype="FP Team",
        ptype="read",
        doc=team_id,
        user=frappe.session.user,
    ):
        raise frappe.PermissionError("You do not have permission to switch to this team")

    set_current_team(team_id, frappe.session.user)
