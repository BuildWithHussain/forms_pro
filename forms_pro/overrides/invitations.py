from urllib.parse import parse_qs, urlparse

import frappe
from frappe.model.document import Document

from forms_pro.utils.teams import set_current_team


def after_accept(invitation: Document, user: Document, user_inserted: bool) -> None:
    """
    Called by Frappe after a User Invitation is accepted.
    Adds the invited user to the team they were invited to and updates the
    in-memory redirect path so the browser lands on /forms (not the API endpoint).
    """
    parsed = urlparse(invitation.redirect_to_path)
    qs = parse_qs(parsed.query)
    team_id = qs.get("team_id", [None])[0]

    if not team_id or not frappe.db.exists("FP Team", team_id):
        return

    from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    if not team.is_team_member(user.name):
        team.add_to_team(user.name)
        team.save(ignore_permissions=True)

    set_current_team(team_id, user.name)

    # Update the in-memory path so _accept_invitation redirects the browser to
    # /forms instead of the API endpoint URL (which breaks when URL-embedded as
    # a redirect_to query param during the password-reset flow).
    invitation.redirect_to_path = "/forms"


def after_insert(doc: Document, method: str) -> None:
    """
    After an invitation is inserted, add the user to the team
    """
    if doc.app_name != "forms_pro":
        return

    role_names = [r.role for r in doc.roles] if doc.roles else []
    if role_names != ["Forms Pro User"]:
        return

    parsed = urlparse(doc.redirect_to_path)
    qs = parse_qs(parsed.query)
    team_id = qs.get("team_id", [None])[0]
    if not team_id:
        return

    # Set the redirect path to add the member to the team (invite_id so API receives it)
    doc.redirect_to_path = f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team_id}&invite_id={doc.name}"
    doc.save(ignore_permissions=True)
