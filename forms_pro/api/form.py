import frappe
from frappe import _
from frappe.share import remove
from pydantic import BaseModel, Field

from forms_pro.api.user import get_user
from forms_pro.forms_pro.doctype.form.form import Form


class FormSharedWithResponse(BaseModel):
    full_name: str
    user_image: str | None
    email: str = Field(alias="user")
    read: bool
    write: bool
    share: bool
    submit: bool


@frappe.whitelist(allow_guest=True)
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


@frappe.whitelist(allow_guest=True)
def get_form_by_route(route: str) -> dict:
    form_id = frappe.db.get_value("Form", {"route": route}, pluck="name")
    return get_form(form_id)


@frappe.whitelist(allow_guest=True)
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
    }


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


@frappe.whitelist()
def get_doctype_fields(doctype: str) -> dict:
    doctype = frappe.get_doc("DocType", doctype)
    fields = doctype.fields

    FIELDTYPES_TO_REMOVE = [
        "Section Break",
        "HTML",
        "Button",
        "Column Break",
        "Tab Break",
        "Barcode",
        "Dynamic Link",
        "Fold",
    ]

    fields = [field for field in fields if field.fieldtype not in FIELDTYPES_TO_REMOVE]

    return fields
