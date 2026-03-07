import frappe
from frappe.core.api.user_invitation import invite_by_email
from frappe.core.doctype.docshare.docshare import DocShare
from frappe.core.doctype.user_invitation.user_invitation import UserInvitation
from frappe.share import get_share_name

from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam, GetTeamMembersResponse
from forms_pro.utils.teams import (
    GetTeamFormsResponseSchema,
    set_current_team,
)
from forms_pro.utils.teams import (
    get_team_forms as get_team_forms_utils,
)


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

    # Clear cache so we read fresh DocShare data (e.g. after toggle_can_edit_team)
    frappe.clear_document_cache("FP Team", team_id)

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    members = team.team_members

    return members


@frappe.whitelist(methods=["POST"])
def create_team(team_name: str, logo_url: str | None = None) -> FPTeam:
    """
    Create a new team

    Args:
        team_name: Name of the team

    Returns:
        FPTeam - The created team
    """

    team: FPTeam = frappe.new_doc("FP Team")
    team.team_name = team_name
    if logo_url:
        team.logo = logo_url
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


@frappe.whitelist(methods=["POST"])
def invite_team_members(team_id: str, emails: list[str]) -> None:
    """
    Invite team members to a team
    """

    if not frappe.has_permission(
        doctype="FP Team",
        ptype="write",
        doc=team_id,
        user=frappe.session.user,
    ):
        raise frappe.PermissionError(
            "You do not have write permission on this team; write access is required to invite members"
        )

    emails_str = ", ".join(emails)

    invite_by_email(
        emails=emails_str,
        roles=["Forms Pro User"],
        redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team_id}",
        app_name="forms_pro",
    )


@frappe.whitelist()
def add_member_to_team_via_invitation(team_id: str, invite_id: str | None = None) -> None:
    """
    Add a member to a team when an invitation is accepted.
    Accepts invite_id from query param (URL may send it as 'id').
    """
    invite_id = invite_id or frappe.form_dict.get("id")
    if not invite_id:
        raise frappe.PermissionError("Invitation id is required")

    invite: UserInvitation = frappe.get_doc("User Invitation", invite_id)

    if invite.status != "Accepted":
        raise frappe.PermissionError("Invitation not accepted")

    if not frappe.has_permission(
        doctype="FP Team",
        ptype="read",
        doc=team_id,
        user=invite.invited_by,
    ):
        raise frappe.PermissionError("You do not have permission to add a member to this team")

    if not frappe.db.exists("User", invite.email):
        raise frappe.PermissionError("User not found")

    team: FPTeam = frappe.get_doc("FP Team", team_id)

    if team.is_team_member(invite.email):
        raise frappe.DuplicateEntryError("User is already a member of the team")

    team.add_to_team(invite.email)
    team.save(ignore_permissions=True)
    set_current_team(team_id, invite.email)

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/forms"


@frappe.whitelist(methods=["POST"])
def toggle_can_edit_team(team_id: str, member_email: str) -> None:
    """
    Toggle the can_edit_team permission for a team member
    """

    if not frappe.has_permission(
        doctype="FP Team",
        ptype="write",
        doc=team_id,
        user=frappe.session.user,
    ):
        raise frappe.PermissionError(
            "You do not have permission to toggle the can_edit_team permission for this team member"
        )

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    if team.owner == member_email:
        raise frappe.PermissionError(
            "The team owner always retains full permissions and cannot have edit access toggled"
        )

    share_name = get_share_name(doctype="FP Team", name=team_id, user=member_email, everyone=0)
    if not share_name:
        raise frappe.PermissionError(
            "You do not have permission to toggle the can_edit_team permission for this team member"
        )

    share: DocShare = frappe.get_doc("DocShare", share_name)
    share.write = not share.write
    share.share = not share.share
    share.save(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def save(team_id: str, fields: dict) -> None:
    """
    Update team fields. Only fields present in the dict are updated.
    """
    frappe.has_permission(
        doctype="FP Team",
        ptype="write",
        doc=team_id,
        user=frappe.session.user,
        throw=True,
    )

    ALLOWED_SAVE_FIELDS = ["team_name", "logo"]

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    for key, value in fields.items():
        if key not in ALLOWED_SAVE_FIELDS:
            frappe.throw(f"Field '{key}' is not allowed")
        setattr(team, key, value)
    team.save()


@frappe.whitelist(methods=["POST"])
def remove_member_from_team(team_id: str, member_email: str) -> None:
    """
    Remove a member from a team
    """

    if not frappe.has_permission(
        doctype="FP Team",
        ptype="write",
        doc=team_id,
        user=frappe.session.user,
    ):
        raise frappe.PermissionError("You do not have permission to remove a member from this team")

    team: FPTeam = frappe.get_doc("FP Team", team_id)
    team.remove_from_team(member_email)
