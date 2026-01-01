import frappe

from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam, GetTeamMembersResponse
from forms_pro.utils.teams import GetTeamFormsResponseSchema
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
    print("team_id", team_id)

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    members = team.team_members

    return members
