# Copyright (c) 2025, harsh@buildwithhussain.com and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

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

        # Clean up test doctype
        if frappe.db.exists("DocType", self.test_doctype_name):
            frappe.delete_doc("DocType", self.test_doctype_name, force=True)

        frappe.db.commit()

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
