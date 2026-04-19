import json
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


def _coerce_field_value(value: Any, fieldtype: str) -> Any:
    """Coerce a submitted value to its comparable type, matching frontend conditionals.ts logic."""
    if value is None or value == "":
        return None
    # Matches isBoolean types in the frontend registry (Switch, Checkbox)
    if fieldtype in ("Switch", "Checkbox"):
        return bool(value)
    if fieldtype == "Number":
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return str(value)


def _evaluate_conditions(conditions: list[dict], form_data: dict, field_map: dict) -> bool:
    """Evaluate AND-joined conditions against submitted form data."""
    for condition in conditions:
        fieldname = condition.get("fieldname")
        operator = condition.get("operator")
        expected = condition.get("value")
        field = field_map.get(fieldname)
        if not field:
            return False
        actual = _coerce_field_value(form_data.get(fieldname), field.fieldtype)
        # Coerce the condition's expected value through the same function so
        # types match — avoids str(True)=="True" vs "true" mismatches and
        # str(3.0)=="3.0" vs "3" mismatches for Number fields.
        expected_coerced = _coerce_field_value(expected, field.fieldtype)
        if operator == "Is" and actual != expected_coerced:
            return False
        if operator == "Is Not" and actual == expected_coerced:
            return False
        if operator == "Is Empty" and actual is not None and actual != "":
            return False
        if operator == "Is Not Empty" and (actual is None or actual == ""):
            return False
    return True


def _validate_form_response(form: "Form", form_data: dict) -> None:
    """
    Validate required and conditionally-required fields server-side.

    Mirrors the shouldFieldBeVisible / shouldFieldBeRequired logic in
    frontend/src/utils/conditionals.ts so that direct API calls cannot
    bypass frontend validation.
    """
    field_map = {f.fieldname: f for f in form.fields}
    errors: list[str] = []

    for field in form.fields:
        is_visible = not field.hidden
        is_required = bool(field.reqd)

        for other in form.fields:
            if not other.conditional_logic:
                continue
            try:
                logic = json.loads(other.conditional_logic)
            except (json.JSONDecodeError, TypeError):
                continue

            if logic.get("target_field") != field.fieldname:
                continue

            conditions_met = _evaluate_conditions(logic.get("conditions", []), form_data, field_map)
            if conditions_met:
                action = logic.get("action")
                if action == "Show Field":
                    is_visible = True
                elif action == "Hide Field":
                    is_visible = False
                elif action == "Require Answer":
                    is_required = True

        if not is_visible:
            continue

        value = form_data.get(field.fieldname)
        is_empty = value is None or value == "" or value == []
        if is_required and is_empty:
            errors.append(_("{0} is required").format(field.label))

    if errors:
        frappe.throw("\n".join(errors), frappe.ValidationError)


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
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
            value = data["value"]
            # JSON fields (e.g. Multiselect) must be stored as a JSON string,
            # but Frappe deserializes request body arrays into Python lists before
            # we get here — serialize them back.
            if isinstance(value, list):
                value = json.dumps(value)
            submission.set(data["fieldname"], value)

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
