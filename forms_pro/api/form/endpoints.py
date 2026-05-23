import frappe
from frappe import _
from frappe.share import add_docshare, remove

from forms_pro.api.user import get_user
from forms_pro.forms_pro.doctype.form.form import Form
from forms_pro.utils.constants import FORMS_PRO_SYSTEM_FIELDNAMES, UNSUPPORTED_FRAPPE_FIELDTYPES
from forms_pro.utils.permissions import require_permission

from .schema import FormSharedWithResponse


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def is_login_required(route: str) -> bool:
    """
    Check if login is enabled for a form.

    args:
        route: str - The route of the form to check.

    returns:
        bool - True if login is required, False otherwise.
    """
    login_enabled = frappe.db.get_value(
        doctype="Form",
        filters={"route": route},
        fieldname="login_required",
    )
    return bool(login_enabled)


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def get_form_by_route(route: str) -> dict:
    form_id = frappe.db.get_value("Form", {"route": route}, pluck="name")
    if not form_id:
        frappe.throw(_("Form not found"), frappe.DoesNotExistError)
    return get_form(form_id)


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def get_form(form_id: str) -> dict:
    form: Form = frappe.get_doc(
        "Form",
        form_id,
    )
    return {
        "name": form.name,
        "title": form.title,
        "description": form.description,
        "fields": form.fields,
        "route": form.route,
        "is_published": form.is_published,
        "allow_incomplete": form.allow_incomplete,
        "linked_doctype": form.linked_doctype,
        "success_title": form.success_title,
        "success_description": form.success_description,
    }


@frappe.whitelist()
@require_permission("Form", "read", param="form_id")
def get_form_for_view(form_id: str) -> dict:
    """Return the form document for the Manage Form page.

    Requires ``read`` permission on the Form. Returns HTTP 404 when the
    form does not exist and HTTP 403 when the user lacks permission.
    """
    return get_form(form_id)


@frappe.whitelist()
@require_permission("Form", "write", param="form_id")
def get_form_for_edit(form_id: str) -> dict:
    """Return the form document for the Edit Form page.

    Requires ``write`` permission on the Form. Returns HTTP 404/403 accordingly.
    """
    return get_form(form_id)


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def get_link_field_options(
    doctype: str,
    filters: dict | None = None,
    page_length: int = 20,
) -> list[str]:
    meta = frappe.get_meta(doctype)
    title_field = meta.title_field or "name"

    results = frappe.get_all(
        doctype=doctype,
        filters=filters or {},
        page_length=page_length,
        fields=["name as value", f"{title_field} as label"],
    )
    return results


@frappe.whitelist()
def get_form_shared_with(form_id: str) -> list[frappe.Any]:
    """
    Get list of users with which a form is shared.

    We validate the current user has read access to the form.
    """
    if not frappe.has_permission(
        "Form",
        "read",
        form_id,
    ):
        frappe.throw(_("You do not have read access to this form"))

    form: Form = frappe.get_doc("Form", form_id)
    shared_with = form.shared_with()

    shared_with_responses = []

    for user in shared_with:
        _user = get_user(user["user"])
        if _user is None:
            continue
        user.update(_user)
        shared_with_responses.append(FormSharedWithResponse.model_validate(user).model_dump())

    return shared_with_responses


@frappe.whitelist()
def remove_form_access(form_id: str, user_email: str) -> None:
    """
    Remove access to a form for a user.

    We validate the current user has write access to the form.

    args:
        form_id: str - The ID of the form to remove access to.
        user_email: str - The email of the user to remove access to.

    """

    if not frappe.has_permission("Form", "write", form_id):
        frappe.throw(_("You do not have write access to this form"))

    return remove(doctype="Form", name=form_id, user=user_email, flags={"ignore_permissions": True})


@frappe.whitelist()
def add_form_access(
    form_id: str,
    user: str,
    read: bool = True,
    write: bool = False,
    share: bool = False,
    submit: bool = False,
) -> None:
    """
    Grant a user access to a form with the specified permissions.

    Uses ``ignore_share_permission`` so the record can be shared regardless of
    the caller's role-level DocShare permissions — the explicit
    ``frappe.has_permission`` check below enforces that only users with share
    access on this particular form can invoke this endpoint.

    Args:
        form_id: Name of the Form document to share.
        user: Email of the user to grant access to.
        read: Allow the user to read the form (default True).
        write: Allow the user to edit the form (default False).
        share: Allow the user to share the form with others (default False).
        submit: Allow the user to submit the form (default False).

    Raises:
        frappe.PermissionError: If the calling user does not have share access
            on the specified form.
    """
    if not frappe.has_permission("Form", "share", form_id):
        frappe.throw(_("You do not have share access to this form"), frappe.PermissionError)

    add_docshare(
        doctype="Form",
        name=form_id,
        user=user,
        read=int(read),
        write=int(write),
        share=int(share),
        submit=int(submit),
        flags={"ignore_share_permission": True},
    )


@frappe.whitelist()
def set_form_permission(
    form_id: str,
    user: str,
    permission_to: str,
    value: bool,
) -> None:
    """
    Toggle a single permission bit for a user on a form.

    Designed for per-toggle updates from the sharing UI — only the specified
    permission field is changed; all other existing permissions are preserved by
    Frappe's ``add_docshare`` merge behaviour.

    Args:
        form_id: Name of the Form document.
        user: Email of the user whose permission is being updated.
        permission_to: Which permission to update. Must be one of:
            ``"read"``, ``"write"``, ``"share"``, ``"submit"``.
        value: ``True`` to grant the permission, ``False`` to revoke it.

    Raises:
        frappe.PermissionError: If the calling user does not have share access
            on the specified form.
        frappe.ValidationError: If ``permission_to`` is not a recognised
            permission type.
    """
    if not frappe.has_permission("Form", "share", form_id):
        frappe.throw(_("You do not have share access to this form"), frappe.PermissionError)

    # Guard against arbitrary kwargs being forwarded to add_docshare
    allowed_permissions = {"read", "write", "share", "submit"}
    if permission_to not in allowed_permissions:
        frappe.throw(_("Invalid permission type"), frappe.ValidationError)

    add_docshare(
        doctype="Form",
        name=form_id,
        user=user,
        **{permission_to: int(bool(value))},
        flags={"ignore_share_permission": True},
    )


@frappe.whitelist()
def get_doctype_list() -> list[str]:
    if not frappe.has_permission("DocType", "read"):
        frappe.throw(_("You do not have read access to this doctype"))

    return frappe.db.get_list(
        "DocType",
        filters={"istable": 0},
        pluck="name",
        order_by="name",
        limit_page_length=99999,
    )


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def get_doctype_fields(doctype: str) -> list:
    doctype = frappe.get_doc("DocType", doctype)
    fields = [
        field
        for field in doctype.fields
        if field.fieldtype not in UNSUPPORTED_FRAPPE_FIELDTYPES
        and field.fieldname not in FORMS_PRO_SYSTEM_FIELDNAMES
    ]
    return fields
