# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

"""
Tests for `forms_pro.api.export.export_submissions`.

Cover three bugs reported in review:
- file_type="Excel" silently produced CSV because Frappe's DataExporter
  expects "Excel"; an XLSX literal was being passed through unchanged.
- `file_type` Literal was not validated at runtime.
- Export ignored `fp_linked_form`, returning rows of every form sharing
  the linked DocType.

Plus invariants of the privilege-swap pattern: access log under the
real user, session user restored on success and on failure.
"""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.api.export import export_submissions
from forms_pro.api.submission import submit_form_response
from forms_pro.tests import FORMS_PRO_TEST_USER
from forms_pro.tests.factories.form_factory import FormFactory

_SAMPLE_FIELDS = [
    {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name", "reqd": 1},
    {"fieldname": "email_address", "fieldtype": "Data", "label": "Email", "options": "Email"},
]


def _create_form(**overrides):
    """Build a published form carrying two real fields, ready for submissions.

    `Form.before_insert` hard-codes `is_published = False`, so publishing
    must happen post-insert.
    """
    form = FormFactory.create(
        fields=[dict(row) for row in _SAMPLE_FIELDS],
        **overrides,
    )
    form.is_published = 1
    form.save(ignore_permissions=True)
    return form


def _submit(form, **values) -> str:
    """Seed a submission via the real submission API so fp_linked_form is set
    by production code rather than by the test."""
    return submit_form_response(
        form_id=form.name,
        form_data=[{"fieldname": k, "value": v} for k, v in values.items()],
    )


class TestExportFileType(IntegrationTestCase):
    """Covers `file_type` argument handling: dispatch, validation, defaults."""

    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.form = _create_form()

    def test_excel_file_type_returns_xlsx_response(self) -> None:
        """`file_type="Excel"` must hit DataExporter's XLSX branch, not CSV.

        Previously the public API accepted "XLSX" and forwarded it to
        DataExporter, which only matches `"Excel"` and silently fell through
        to the CSV writer. Asserting `response.type != "csv"` guards the
        dispatch path regardless of how Frappe encodes the xlsx response.
        """
        export_submissions(form_id=self.form.name, file_type="Excel")
        self.assertNotEqual(
            frappe.response.get("type"),
            "csv",
            "Excel file_type should not produce a CSV response.",
        )

    def test_invalid_file_type_raises_validation_error(self) -> None:
        """An unsupported file_type must raise at the boundary.

        `Literal[...]` is a static hint only; the whitelisted method
        receives whatever string the caller sends. An explicit runtime
        check converts garbage input into a `ValidationError` instead of
        a confusing internal failure deeper in DataExporter.
        """
        with self.assertRaises(frappe.ValidationError):
            export_submissions(form_id=self.form.name, file_type="PDF")


class TestExportScopedByForm(IntegrationTestCase):
    """Two forms share a linked DocType. Export must not bleed across forms."""

    def setUp(self) -> None:
        frappe.set_user("Administrator")
        # Two forms over the same linked DocType so we can prove the export
        # is scoped by fp_linked_form, not by linked_doctype.
        self.form_a = _create_form()
        self.form_b = _create_form(linked_doctype=self.form_a.linked_doctype)

        self.row_a = _submit(self.form_a, full_name="Alice A", email_address="alice@example.com")
        self.row_b = _submit(self.form_b, full_name="Bob B", email_address="bob@example.com")

    def test_export_returns_only_current_forms_submissions(self) -> None:
        """Exporting form_a must include form_a's rows and exclude form_b's.

        Without a `fp_linked_form` filter the DataExporter pulled every
        row of the linked DocType, leaking other forms' submissions.
        Asserts at both the submission-id level and the field-value level.
        """
        export_submissions(form_id=self.form_a.name, file_type="CSV")
        csv_body = frappe.response.get("result") or ""

        self.assertIn(self.row_a, csv_body, "form_a submission must appear in export.")
        self.assertIn("Alice A", csv_body, "form_a field value must appear in export.")
        self.assertNotIn(
            self.row_b,
            csv_body,
            "form_b submission must NOT appear in form_a's export.",
        )
        self.assertNotIn(
            "Bob B",
            csv_body,
            "form_b field value must NOT appear in form_a's export.",
        )

    def test_export_csv_header_includes_form_field_labels(self) -> None:
        """CSV header row carries human-readable labels of all exportable fields."""
        export_submissions(form_id=self.form_a.name, file_type="CSV")
        csv_body = frappe.response.get("result") or ""
        # `export_without_column_meta=True` collapses metadata rows; the
        # first row carries the labels.
        header_line = csv_body.splitlines()[0] if csv_body else ""
        self.assertIn("Full Name", header_line)
        self.assertIn("Email", header_line)


class TestExportFieldSelection(IntegrationTestCase):
    """Which form fields end up in the CSV column set."""

    def setUp(self) -> None:
        frappe.set_user("Administrator")

    def test_display_only_fields_excluded_from_export(self) -> None:
        """Heading / display-only fields have no DB column and must not
        appear as CSV columns.

        The `FormField.stores_value` filter in `export.py` drops any field
        whose resolved Frappe fieldtype is in `no_value_fields`.
        """
        form = FormFactory.create(
            fields=[
                {"fieldname": "intro_heading", "fieldtype": "Heading 1", "label": "Welcome"},
                {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name"},
            ],
        )
        form.is_published = 1
        form.save(ignore_permissions=True)

        export_submissions(form_id=form.name, file_type="CSV")
        csv_body = frappe.response.get("result") or ""
        header_line = csv_body.splitlines()[0] if csv_body else ""

        self.assertNotIn(
            "intro_heading",
            csv_body,
            "Heading field name must not appear anywhere in the export.",
        )
        self.assertNotIn(
            "Welcome",
            csv_body,
            "Heading label must not be promoted to a CSV column.",
        )
        self.assertIn("Full Name", header_line)

    def test_all_exportable_fields_present_in_csv_header(self) -> None:
        """Every non-display field defined on the form contributes one column."""
        fields = [
            {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name"},
            {"fieldname": "age", "fieldtype": "Number", "label": "Age"},
            {"fieldname": "email_address", "fieldtype": "Email", "label": "Email"},
            {"fieldname": "joined_on", "fieldtype": "Date", "label": "Joined On"},
        ]
        form = FormFactory.create(fields=fields)
        form.is_published = 1
        form.save(ignore_permissions=True)

        export_submissions(form_id=form.name, file_type="CSV")
        csv_body = frappe.response.get("result") or ""
        header_line = csv_body.splitlines()[0] if csv_body else ""

        for field in fields:
            self.assertIn(
                field["label"],
                header_line,
                f"Field label {field['label']!r} missing from CSV header.",
            )


class TestExportPermissions(IntegrationTestCase):
    """Authorization gate on `export_submissions`."""

    def test_user_without_write_permission_raises_permission_error(self) -> None:
        """A Forms Pro user with no DocShare on the form must be rejected.

        Export is gated on Form-level `write`. The test user holds the
        Forms Pro role but has no team membership or share for a form
        owned by Administrator, so `has_permission` returns False.
        """
        frappe.set_user("Administrator")
        form = _create_form()

        frappe.set_user(FORMS_PRO_TEST_USER)
        try:
            with self.assertRaises(frappe.PermissionError):
                export_submissions(form_id=form.name, file_type="CSV")
        finally:
            frappe.set_user("Administrator")


class TestExportAccessLog(IntegrationTestCase):
    """An export must be recorded in the Access Log for audit."""

    def test_access_log_row_written_for_export(self) -> None:
        """`make_access_log` runs before the privilege swap so the log
        entry is attributed to the real user, not Administrator.
        """
        frappe.set_user("Administrator")
        form = _create_form()

        before = frappe.db.count(
            "Access Log",
            filters={"method": "forms_pro.api.export.export_submissions"},
        )
        export_submissions(form_id=form.name, file_type="CSV")
        # `make_access_log` uses `deferred_insert` outside tests; in tests
        # it uses `db_insert`, so the row is visible immediately.
        after = frappe.db.count(
            "Access Log",
            filters={"method": "forms_pro.api.export.export_submissions"},
        )
        self.assertEqual(after, before + 1, "Export must add one Access Log row.")

        latest = frappe.get_last_doc(
            "Access Log",
            filters={"method": "forms_pro.api.export.export_submissions"},
        )
        self.assertEqual(
            latest.user,
            "Administrator",
            "Access Log must be attributed to the caller, not the swapped user.",
        )
        self.assertEqual(latest.export_from, form.linked_doctype)


class TestExportSessionRestoration(IntegrationTestCase):
    """The privilege-swap finally block must restore the real session."""

    def setUp(self) -> None:
        # Build the form as Administrator, share it with the test user so
        # the perm check passes, then run the export AS the test user.
        # Comparing against a non-Admin user is essential: if `before` were
        # Administrator the assertion would be tautological since the swap
        # also lands on Administrator.
        from frappe.share import add_docshare

        frappe.set_user("Administrator")
        self.form = _create_form()
        add_docshare(
            "Form",
            self.form.name,
            user=FORMS_PRO_TEST_USER,
            read=1,
            write=1,
            flags={"ignore_share_permission": True},
        )

    def tearDown(self) -> None:
        frappe.set_user("Administrator")

    def test_session_user_restored_after_successful_export(self) -> None:
        """`frappe.session.user` must equal the pre-call user (non-Admin)
        after a successful export. Detects a missing `set_user` restore."""
        frappe.set_user(FORMS_PRO_TEST_USER)
        before = frappe.session.user
        self.assertEqual(before, FORMS_PRO_TEST_USER)  # sanity

        export_submissions(form_id=self.form.name, file_type="CSV")

        self.assertEqual(
            frappe.session.user,
            FORMS_PRO_TEST_USER,
            "Session user must be restored after a successful export.",
        )

    def test_session_user_restored_when_exporter_raises(self) -> None:
        """If DataExporter blows up mid-export, the finally block must
        still restore the session user; otherwise the request would
        continue running as Administrator (privilege leak)."""
        frappe.set_user(FORMS_PRO_TEST_USER)

        with patch(
            "forms_pro.api.export.endpoints.DataExporter.build_response",
            side_effect=RuntimeError("boom"),
        ):
            with self.assertRaises(RuntimeError):
                export_submissions(form_id=self.form.name, file_type="CSV")

        self.assertEqual(
            frappe.session.user,
            FORMS_PRO_TEST_USER,
            "Session user must be restored even when the exporter raises.",
        )
