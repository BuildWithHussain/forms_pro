import frappe

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
