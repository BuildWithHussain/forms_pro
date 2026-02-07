import frappe
from frappe.core.doctype.user.user import User

from forms_pro.roles import FORMS_PRO_ROLE
from forms_pro.utils.teams import get_user_teams


def has_forms_pro_permission() -> bool:
    if frappe.session.user == "Administrator":
        return True

    user_roles = frappe.get_roles(frappe.session.user)
    return FORMS_PRO_ROLE in user_roles


def handle_forms_pro_role_change(doc, method) -> None:
    user: User = frappe.get_doc("User", doc.name)
    user.on_update()

    if user.has_value_changed("roles"):
        try:
            doc_before_save = user.get_doc_before_save()
        except AttributeError:
            doc_before_save = None

        roles_before_save = doc_before_save.get("roles") if doc_before_save else []
        roles_after_save = user.get("roles")

        has_forms_pro_role_before_save = any(role.role == FORMS_PRO_ROLE for role in roles_before_save)
        has_forms_pro_role_after_save = any(role.role == FORMS_PRO_ROLE for role in roles_after_save)

        if not has_forms_pro_role_before_save and has_forms_pro_role_after_save:
            if len(get_user_teams(user.name)) > 0:
                return
            create_default_team_for_user(user)


def create_default_team_for_user(user: User) -> None:
    from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam

    team: FPTeam = frappe.new_doc("FP Team")
    team.team_name = f"{user.first_name}'s Team"
    team.insert(ignore_permissions=True)
    team.append(
        "users",
        {
            "user": user.name,
        },
    )
    team.save(ignore_permissions=True)
