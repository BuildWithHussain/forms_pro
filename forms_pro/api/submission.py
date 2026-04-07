from datetime import datetime
from typing import Any

import frappe
from frappe import _
from frappe.share import add_docshare
from pydantic import BaseModel, Field, field_validator

from forms_pro.forms_pro.doctype.form.form import Form
from forms_pro.utils.form_generator import SubmissionStatus


class UserSubmissionResponse(BaseModel):
    name: str = Field(description="Name of the submission")
    creation: datetime = Field(description="Creation date of the submission")
    modified: datetime = Field(description="Last modified date of the submission")
    submission_status: str = Field(
        description="Status of the submission",
        alias="fp_submission_status",
        default=SubmissionStatus.SUBMITTED.value,
    )
    owner: str = Field(description="Owner of the submission")

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
def submit_form_response(
    form_id: str,
    form_data: list[dict],
    submission_status: SubmissionStatus = SubmissionStatus.SUBMITTED,
) -> str:
    """
    Submit a form response

    Args:
        form_id: The ID of the form
        form_data: The data of the form
        submission_status: The status of the submission: Default is `Submitted`

    Returns:
        The name of the submission
    """
    try:
        form: Form = frappe.get_doc("Form", form_id)
        linked_doctype = form.linked_doctype

        if not form.is_published:
            frappe.throw(
                _("This form is un-published, so responses are no longer being collected."),
                frappe.PermissionError,
            )

        submission = frappe.new_doc(linked_doctype)
        for data in form_data:
            submission.set(data["fieldname"], data["value"])

        submission.fp_linked_form = form_id
        submission.fp_submission_status = submission_status.value
        submission.insert(ignore_permissions=True, ignore_mandatory=True)

        # Share the submission with the owner
        add_docshare(
            doctype=linked_doctype,
            name=submission.name,
            user=frappe.session.user,
            read=1,
            write=1,
            flags={
                "ignore_share_permission": True,
            },
        )

        return submission.name
    except Exception:
        raise


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

    submissions = frappe.get_all(
        doctype=linked_doctype,
        filters={"owner": frappe.session.user},
        fields=["name", "creation", "modified", "fp_submission_status", "owner"],
        order_by="creation",
    )

    return [UserSubmissionResponse.model_validate(submission).model_dump() for submission in submissions]


@frappe.whitelist()
def get_submission_response(submission_id: str, doctype: str) -> dict[str, Any]:
    """
    Get a full submission response by ID.
    This API checks if the user is the team member / the form is shared with the user.

    Args:
        submission_id: The name/ID of the submission document
        doctype: The submission's doctype (linked_doctype of the form)

    Returns:
        The submission document as a dict
    """
    linked_form = frappe.db.get_value(doctype, submission_id, "fp_linked_form")
    if not linked_form:
        frappe.throw(_("Submission not found."), frappe.DoesNotExistError)

    form_data = frappe.db.get_value("Form", linked_form, ["linked_team_id", "linked_doctype"], as_dict=True)

    if form_data.linked_doctype != doctype:
        frappe.throw(_("Invalid doctype for this submission."), frappe.PermissionError)

    if not frappe.has_permission(
        doctype="FP Team", ptype="write", doc=form_data.linked_team_id, user=frappe.session.user
    ):
        frappe.throw(
            _("You do not have permission to read this form's submissions."),
            frappe.PermissionError,
        )

    submission = frappe.get_doc(form_data.linked_doctype, submission_id)
    return submission.as_dict()


@frappe.whitelist()
def get_submission(submission_doctype: str, submission_name: str) -> dict[str, Any]:
    """
    Get a submission by name. Used usually by the form owner to view the submission details.

    Args:
        submission_name: The name of the submission

    Returns:
        The submission
    """
    submission = frappe.get_doc(submission_doctype, submission_name)

    if not frappe.has_permission(doctype=submission.doctype, ptype="read", doc=submission.name):
        frappe.throw(
            _("You do not have permission to read this submission."),
            frappe.PermissionError,
        )

    return submission.as_dict()


@frappe.whitelist()
def get_all_submissions(form_id: str) -> list[UserSubmissionResponse]:
    """
    Get all submissions for a form

    Args:
        form_id: The ID of the form

    Returns:
        A list of submissions for the form
    """
    linked_team = frappe.db.get_value("Form", form_id, "linked_team_id")

    if not linked_team:
        frappe.throw(_("Form not found."), frappe.DoesNotExistError)

    if not frappe.has_permission(doctype="FP Team", ptype="write", doc=linked_team, user=frappe.session.user):
        frappe.throw(
            _("You do not have permission to read this form's submissions."),
            frappe.PermissionError,
        )

    form: Form = frappe.get_doc("Form", form_id)
    linked_doctype = form.linked_doctype

    submissions = frappe.get_all(
        doctype=linked_doctype,
        fields=["name", "creation", "modified", "fp_submission_status", "owner"],
        filters={"fp_submission_status": "Submitted"},
        order_by="creation",
    )

    return [UserSubmissionResponse.model_validate(submission).model_dump() for submission in submissions]
