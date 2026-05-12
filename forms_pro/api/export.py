from typing import Literal

import frappe
from frappe import _
from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.core.doctype.data_export.exporter import DataExporter
from werkzeug.utils import secure_filename

from forms_pro.forms_pro.doctype.form.form import Form

_SUPPORTED_FILE_TYPES = ("CSV", "Excel")


@frappe.whitelist()
def export_submissions(form_id: str, file_type: Literal["CSV", "Excel"] = "CSV") -> None:
    """
    Export submissions for a form as a CSV or XLSX download.

    Permission model: gated on `write` on the Form doctype only.
    Frappe's `DataExporter` enforces `can_export` on the linked DocType,
    which our app deliberately does not grant at the role level (Forms Pro
    permissions live on the Form, not on the linked DocType). To bridge
    that gap we run the exporter as Administrator and restore the original
    session user in `finally`. The Form-level permission check above is
    the real authorization gate.
    """
    # `Literal` is not enforced at runtime; validate explicitly.
    if file_type not in _SUPPORTED_FILE_TYPES:
        frappe.throw(
            _("Unsupported file_type {0}. Allowed: {1}.").format(file_type, ", ".join(_SUPPORTED_FILE_TYPES)),
            frappe.ValidationError,
        )

    if not frappe.has_permission(doctype="Form", ptype="write", doc=form_id):
        frappe.throw(
            _("You do not have permission to export submissions for this form."),
            frappe.PermissionError,
        )

    form: Form = frappe.get_doc("Form", form_id)
    linked_doctype = form.linked_doctype

    columns = [
        "name",
        "creation",
        "owner",
        "fp_submission_status",
        *[field.fieldname for field in form.fields if field.stores_value],
    ]
    select_columns = {linked_doctype: columns}

    # Audit the export under the real (non-Admin) user before the swap.
    make_access_log(
        doctype=linked_doctype,
        file_type=file_type,
        columns=frappe.as_json(columns),
        method="forms_pro.api.export.export_submissions",
    )

    # `frappe.set_user` is built for background jobs, not web requests: it
    # overwrites `local.session.sid` with the username AND wipes
    # `local.session.data` (which holds `last_updated`, `lang`, csrf token).
    # After the response, `Session.update()` persists that empty data into
    # the DB row + cache; the next request then sees `last_updated=None`,
    # the expiry check treats the session as expired, the row is deleted,
    # and the user is logged out. Snapshot user / sid / data and restore
    # all three after the privilege swap.
    saved_user = frappe.session.user
    saved_sid = frappe.session.sid
    saved_data = frappe.session.data
    try:
        # Authorization is already enforced via `has_permission("Form", "write", ...)`
        # above. The swap bypasses `can_export` on the linked DocType (intentionally
        # not granted at the role level in Forms Pro). Session state is snapshotted
        # immediately above and fully restored in `finally`. Audited 2026-05-13.
        frappe.set_user("Administrator")  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-setuser
        exporter = DataExporter(
            doctype=linked_doctype,
            all_doctypes=False,
            with_data=True,
            select_columns=frappe.as_json(select_columns),
            # Scope strictly to this form. Without a filter `DataExporter`
            # pulls every row of `linked_doctype`, leaking submissions of
            # other forms that share the same DocType.
            filters=frappe.as_json({"fp_linked_form": form_id}),
            file_type=file_type,
            export_without_column_meta=True,
        )
        exporter.build_response()
        # Override filename so the download reads as form-specific, not the
        # underlying DocType name. Title may contain chars that are illegal
        # on Windows/macOS filesystems (e.g. `! / : ? *`); `secure_filename`
        # strips them. Falls back to form_id when title sanitizes to empty.
        # CSV reads `frappe.response["doctype"]` (via `as_csv`); Excel reads
        # `frappe.response["filename"]` (via `provide_binary_file`). Set both.
        safe_title = secure_filename(form.title or "") or form_id
        timestamp = frappe.utils.now_datetime().strftime("%Y-%m-%d_%H%M%S")
        base_name = f"Submissions_{safe_title}_{timestamp}"
        frappe.response["doctype"] = base_name
        if file_type == "Excel":
            frappe.response["filename"] = f"{base_name}.xlsx"
    finally:
        try:
            frappe.set_user(saved_user)  # nosemgrep: frappe-semgrep-rules.rules.security.frappe-setuser
        except Exception:
            frappe.log_error(title="export_submissions: failed to restore user")
        frappe.local.session.sid = saved_sid
        frappe.local.session.data = saved_data
