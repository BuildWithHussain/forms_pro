# Copyright (c) 2025, harsh@buildwithhussain.com and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.patches.v0_x.backfill_field_layout import execute as backfill_execute
from forms_pro.utils.teams import get_user_teams

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestForm(IntegrationTestCase):
    def setUp(self):
        """Set up test data before each test method."""
        # Create a test DocType for testing
        self.test_doctype_name = "Test Form DocType"
        self.create_test_doctype()

        self.test_user = "test_forms_pro_user@example.com"
        self.test_team = get_user_teams(self.test_user)[0]["name"]

        # Create a test Form
        self.test_form = frappe.get_doc(
            {
                "doctype": "Form",
                "title": "Test Form",
                "linked_doctype": self.test_doctype_name,
                "fields": [],
                "linked_team_id": self.test_team,
            }
        )
        self.test_form.insert()

    def tearDown(self):
        """Clean up test data after each test method."""
        # Clean up test form
        if frappe.db.exists("Form", self.test_form.name):
            self.test_form.delete()

        # Clean up test doctype - delete_doc on DocType triggers DDL which auto-commits
        if frappe.db.exists("DocType", self.test_doctype_name):
            frappe.delete_doc("DocType", self.test_doctype_name, force=True)

    def create_test_doctype(self):
        """Create a test DocType with some initial fields."""
        if frappe.db.exists("DocType", self.test_doctype_name):
            return

        doctype = frappe.get_doc(
            {
                "doctype": "DocType",
                "name": self.test_doctype_name,
                "module": "Custom",
                "custom": 1,
                "fields": [
                    {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
                    {"fieldname": "description", "fieldtype": "Text", "label": "Description"},
                ],
            }
        )
        doctype.insert()

    def test_add_new_field(self):
        """Test adding a new field to the doctype."""
        # Add a new field to the form
        self.test_form.append(
            "fields", {"label": "Email Address", "fieldname": "email", "fieldtype": "Email", "reqd": 1}
        )
        self.test_form.save()

        # Check if the field was added to the doctype
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        field_names = [f.fieldname for f in doctype_doc.fields]

        self.assertIn("email", field_names)

        # Check field properties
        email_field = next(f for f in doctype_doc.fields if f.fieldname == "email")
        self.assertEqual(email_field.label, "Email Address")
        self.assertEqual(email_field.fieldtype, "Data")
        self.assertEqual(email_field.reqd, 1)

    def test_fieldname_change(self):
        """Test changing a fieldname by matching label."""
        # First add a field with original fieldname
        self.test_form.append(
            "fields", {"label": "User Name", "fieldname": "user_name", "fieldtype": "Data", "reqd": 1}
        )
        self.test_form.save()

        # Now change the fieldname but keep the same label
        self.test_form.fields[0].fieldname = "username"
        self.test_form.save()

        # Check if the fieldname was updated in the doctype
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        field_names = [f.fieldname for f in doctype_doc.fields]

        self.assertNotIn("user_name", field_names)
        self.assertIn("username", field_names)

        # Check that the field with new fieldname has correct properties
        username_field = next(f for f in doctype_doc.fields if f.fieldname == "username")
        self.assertEqual(username_field.label, "User Name")
        self.assertEqual(username_field.fieldtype, "Data")
        self.assertEqual(username_field.reqd, 1)

    def test_update_existing_field_properties(self):
        """Test updating properties of an existing field."""
        # Add a field
        self.test_form.append(
            "fields",
            {
                "label": "Phone Number",
                "fieldname": "phone",
                "fieldtype": "Data",
                "reqd": 0,
                "description": "Enter phone number",
            },
        )
        self.test_form.save()

        # Update field properties
        self.test_form.fields[0].reqd = 1
        self.test_form.fields[0].description = "Enter your phone number"
        self.test_form.fields[0].fieldtype = "Data"
        self.test_form.save()

        # Check if properties were updated
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        phone_field = next(f for f in doctype_doc.fields if f.fieldname == "phone")

        self.assertEqual(phone_field.reqd, 1)
        self.assertEqual(phone_field.description, "Enter your phone number")
        self.assertEqual(phone_field.fieldtype, "Data")

    def test_multiple_fields_operations(self):
        """Test multiple field operations: add, rename, and update."""
        # Add multiple fields
        self.test_form.append(
            "fields", {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "reqd": 1}
        )
        self.test_form.append(
            "fields", {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data", "reqd": 1}
        )
        self.test_form.append(
            "fields", {"label": "Age", "fieldname": "age", "fieldtype": "Number", "reqd": 0}
        )
        self.test_form.save()

        # Verify all fields were added
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        field_names = [f.fieldname for f in doctype_doc.fields]

        self.assertIn("first_name", field_names)
        self.assertIn("last_name", field_names)
        self.assertIn("age", field_names)

        # Now rename one field and update another
        self.test_form.fields[0].fieldname = "fname"  # Rename first_name to fname
        self.test_form.fields[2].reqd = 1  # Make age required
        self.test_form.save()

        # Verify changes
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        field_names = [f.fieldname for f in doctype_doc.fields]

        self.assertNotIn("first_name", field_names)
        self.assertIn("fname", field_names)
        self.assertIn("last_name", field_names)
        self.assertIn("age", field_names)

        # Check specific field properties
        fname_field = next(f for f in doctype_doc.fields if f.fieldname == "fname")
        age_field = next(f for f in doctype_doc.fields if f.fieldname == "age")

        self.assertEqual(fname_field.label, "First Name")
        self.assertEqual(age_field.reqd, 1)

    def test_field_with_options(self):
        """Test adding a field with options (Select field)."""
        self.test_form.append(
            "fields",
            {
                "label": "Status",
                "fieldname": "status",
                "fieldtype": "Select",
                "options": "Active\nInactive\nPending",
                "default": "Active",
            },
        )
        self.test_form.save()

        # Check if field was added with correct options
        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        status_field = next(f for f in doctype_doc.fields if f.fieldname == "status")

        self.assertEqual(status_field.fieldtype, "Select")
        self.assertEqual(status_field.options, "Active\nInactive\nPending")
        self.assertEqual(status_field.default, "Active")

    def test_layout_fields_do_not_affect_doctype_sync(self):
        """Changing row_index/column_index on FormField must not modify the linked DocType."""
        self.test_form.append(
            "fields",
            {"label": "Full Name", "fieldname": "full_name", "fieldtype": "Data"},
        )
        self.test_form.save()

        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        fields_before = [(f.fieldname, f.fieldtype, f.label) for f in doctype_doc.fields]

        # Mutate only layout fields and save
        self.test_form.fields[0].row_index = 5
        self.test_form.fields[0].column_index = 3
        self.test_form.save()

        doctype_doc = frappe.get_doc("DocType", self.test_doctype_name)
        fields_after = [(f.fieldname, f.fieldtype, f.label) for f in doctype_doc.fields]

        self.assertEqual(fields_before, fields_after)


class TestBackfillFieldLayoutPatch(IntegrationTestCase):
    """Backfill patch sets row_index = idx-1, column_index = 0 for all FormField rows."""

    _test_doctype_name = "Backfill Patch Test DocType"

    def setUp(self):
        from forms_pro.tests import FORMS_PRO_TEST_USER
        from forms_pro.utils.teams import get_user_teams

        if not frappe.db.exists("DocType", self._test_doctype_name):
            frappe.get_doc(
                {
                    "doctype": "DocType",
                    "name": self._test_doctype_name,
                    "module": "Custom",
                    "custom": 1,
                    "fields": [{"fieldname": "title", "fieldtype": "Data", "label": "Title"}],
                }
            ).insert()

        self.test_team = get_user_teams(FORMS_PRO_TEST_USER)[0]["name"]

    def tearDown(self):
        for name in frappe.get_all("Form", filters={"linked_doctype": self._test_doctype_name}, pluck="name"):
            frappe.delete_doc("Form", name, force=True, ignore_permissions=True)
        if frappe.db.exists("DocType", self._test_doctype_name):
            frappe.delete_doc("DocType", self._test_doctype_name, force=True)

    def _make_form(self) -> str:
        form = frappe.get_doc(
            {
                "doctype": "Form",
                "title": "Patch Test Form",
                "linked_doctype": self._test_doctype_name,
                "linked_team_id": self.test_team,
                "fields": [
                    {"label": "Field A", "fieldname": "field_a", "fieldtype": "Data"},
                    {"label": "Field B", "fieldname": "field_b", "fieldtype": "Data"},
                    {"label": "Field C", "fieldname": "field_c", "fieldtype": "Data"},
                ],
            }
        )
        form.insert(ignore_permissions=True)
        return form.name

    def test_patch_sets_row_index_from_idx(self):
        form_name = self._make_form()
        frappe.db.sql(
            "UPDATE `tabForm Field` SET row_index = 99, column_index = 99 WHERE parent = %s",
            form_name,
        )

        backfill_execute()

        fields = frappe.get_all(
            "Form Field",
            filters={"parent": form_name},
            fields=["fieldname", "idx", "row_index", "column_index"],
            order_by="idx asc",
        )
        for f in fields:
            self.assertEqual(f.row_index, f.idx - 1, f"row_index wrong for {f.fieldname}")
            self.assertEqual(f.column_index, 0, f"column_index wrong for {f.fieldname}")

    def test_patch_is_idempotent(self):
        form_name = self._make_form()
        backfill_execute()
        backfill_execute()

        fields = frappe.get_all(
            "Form Field",
            filters={"parent": form_name},
            fields=["idx", "row_index", "column_index"],
            order_by="idx asc",
        )
        for f in fields:
            self.assertEqual(f.row_index, f.idx - 1)
            self.assertEqual(f.column_index, 0)
