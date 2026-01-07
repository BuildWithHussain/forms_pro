from datetime import datetime
from typing import Any

import frappe
from frappe.model.document import Document
from frappe.share import add_docshare
from pydantic import BaseModel, Field, field_validator

from forms_pro.forms_pro.doctype.form.form import Form


class UserSubmissionResponse(BaseModel):
    name: str = Field(description="Name of the submission")
    creation: datetime = Field(description="Creation date of the submission")
    modified: datetime = Field(description="Last modified date of the submission")

    @field_validator("creation", "modified", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Convert datetime string to datetime object."""
        if isinstance(v, str):
            return frappe.utils.get_datetime(v)
        if isinstance(v, datetime):
            return v
        raise ValueError(f"Invalid datetime value: {v}")


@frappe.whitelist(allow_guest=True)
def submit_form_response(form_id: str, form_data: list[dict]) -> str:
    """
    Submit a form response

    Args:
        form_id: The ID of the form
        form_data: The data of the form

    Returns:
        The name of the submission
    """
    form: Form = frappe.get_doc("Form", form_id)
    linked_doctype = form.linked_doctype

    submission = frappe.new_doc(linked_doctype)
    for data in form_data:
        submission.set(data["fieldname"], data["value"])
    submission.insert(ignore_permissions=True)

    # Share the submission with the owner
    add_docshare(
        doctype=linked_doctype,
        name=submission.name,
        user=frappe.session.user,
        read=1,
        write=1,
        submit=1,
        flags={
            "ignore_share_permission": True,
        },
    )

    return submission.name


@frappe.whitelist()
def get_user_submissions(form_id: str) -> list[UserSubmissionResponse]:
    """
    Get the submissions for a user

    Args:
        form_id: The ID of the form

    Returns:
        A list of submissions for the user
    """

    if frappe.session.user == "Guest":
        return []

    form: Form = frappe.get_doc("Form", form_id)
    linked_doctype = form.linked_doctype

    submissions = frappe.db.get_all(
        doctype=linked_doctype,
        filters={"owner": frappe.session.user},
        fields=["name", "creation", "modified"],
        order_by="creation desc",
    )

    return [UserSubmissionResponse.model_validate(submission).model_dump() for submission in submissions]
