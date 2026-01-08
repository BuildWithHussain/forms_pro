# Copyright (c) 2025, harsh@buildwithhussain.com and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.utils.form_generator import FormGenerator
from forms_pro.utils.teams import get_user_teams


class IntegrationTestFormGenerator(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.test_user = "test_forms_pro_user@example.com"
        self.test_team = get_user_teams(self.test_user)[0]["name"]

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def test_form_generator_initialization_with_doctype(self):
        """Test FormGenerator initialization with existing DocType"""
        # Create a test DocType
        test_doctype = frappe.new_doc("DocType")
        test_doctype.name = "Test DocType" + frappe.utils.random_string(8)
        test_doctype.module = "Forms Pro"
        test_doctype.custom = True
        test_doctype.insert(ignore_permissions=True)

        # Initialize FormGenerator with existing DocType
        form_generator = FormGenerator(linked_doctype=test_doctype.name, team_id=self.test_team)

        # Assertions
        self.assertIsNotNone(form_generator.doctype)
        self.assertEqual(form_generator.doctype.name, test_doctype.name)
        self.assertEqual(form_generator.doctype.module, "Forms Pro")

    def test_form_generator_initialization_without_doctype(self):
        """Test FormGenerator initialization without DocType"""
        form_generator = FormGenerator(team_id=self.test_team)

        # Assertions
        self.assertIsNone(form_generator.doctype)

    def test_generate_doctype_name_format(self):
        """Test that generate_doctype_name returns correct format"""
        form_generator = FormGenerator(team_id=self.test_team)
        doctype_name = form_generator._generate_doctype_name()

        # Assertions
        self.assertTrue(doctype_name.startswith("formspro_"))
        self.assertEqual(len(doctype_name), 21)  # formspro_ + 6 random chars + 6 digits
        self.assertTrue(doctype_name[9:15].isalnum())  # Random string part
        self.assertTrue(doctype_name[15:].isdigit())  # Serial number part

    def test_generate_doctype_name_uniqueness(self):
        """Test that generate_doctype_name generates unique names"""
        form_generator = FormGenerator(team_id=self.test_team)
        names = set()

        # Generate multiple names and check uniqueness
        for _ in range(5):
            name = form_generator._generate_doctype_name()
            self.assertNotIn(name, names)
            names.add(name)

    def test_generate_creates_doctype_when_none_provided(self):
        """Test that generate() creates a new DocType when none is provided"""
        form_generator = FormGenerator(team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Assertions
        self.assertIsNotNone(form_generator.doctype)
        self.assertTrue(form_generator.doctype.name.startswith("formspro_"))
        self.assertEqual(form_generator.doctype.module, "User Forms")
        self.assertTrue(form_generator.doctype.custom)
        self.assertTrue(form_generator.doctype.track_changes)
        self.assertTrue(form_generator.doctype.track_views)
        self.assertFalse(form_generator.doctype.index_web_pages_for_search)

        # Verify DocType exists in database
        self.assertTrue(frappe.db.exists("DocType", form_generator.doctype.name))

    def test_generate_uses_existing_doctype_when_provided(self):
        """Test that generate() uses existing DocType when provided"""
        # Create a test DocType
        test_doctype = frappe.new_doc("DocType")
        test_doctype.name = "Test" + frappe.utils.random_string(8)
        test_doctype.module = "Forms Pro"
        test_doctype.custom = True
        test_doctype.insert(ignore_permissions=True)

        form_generator = FormGenerator(linked_doctype=test_doctype.name, team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Assertions
        self.assertEqual(form_generator.doctype.name, test_doctype.name)
        self.assertIsNotNone(form_generator.form_document)

    def test_generate_creates_form_document(self):
        """Test that generate() creates a Form document"""
        form_generator = FormGenerator(team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Assertions
        self.assertIsNotNone(form_generator.form_document)
        self.assertEqual(form_generator.form_document.linked_doctype, form_generator.doctype.name)

        # Verify Form document exists in database
        self.assertTrue(frappe.db.exists("Form", form_generator.form_document.name))

    def test_generate_complete_flow(self):
        """Test the complete flow of FormGenerator.generate()"""
        form_generator = FormGenerator(team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Assertions for complete flow
        self.assertIsNotNone(form_generator.doctype)
        self.assertIsNotNone(form_generator.form_document)
        self.assertEqual(form_generator.form_document.linked_doctype, form_generator.doctype.name)

        # Verify both documents exist in database
        self.assertTrue(frappe.db.exists("DocType", form_generator.doctype.name))
        self.assertTrue(frappe.db.exists("Form", form_generator.form_document.name))

        # Verify DocType properties
        self.assertTrue(form_generator.doctype.name.startswith("formspro_"))
        self.assertEqual(form_generator.doctype.module, "User Forms")
        self.assertTrue(form_generator.doctype.custom)

    def test_generate_with_existing_doctype_complete_flow(self):
        """Test complete flow when DocType is provided during initialization"""
        # Create a test DocType
        test_doctype = frappe.new_doc("DocType")
        test_doctype.name = "Test" + frappe.utils.random_string(8)
        test_doctype.module = "Forms Pro"
        test_doctype.custom = True
        test_doctype.insert(ignore_permissions=True)

        form_generator = FormGenerator(linked_doctype=test_doctype.name, team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Assertions
        self.assertEqual(form_generator.doctype.name, test_doctype.name)
        self.assertIsNotNone(form_generator.form_document)
        self.assertEqual(form_generator.form_document.linked_doctype, form_generator.doctype.name)

        # Verify Form document exists in database
        self.assertTrue(frappe.db.exists("Form", form_generator.form_document.name))

    def test_generate_creates_doctype_docshare(self):
        """Test that generate() creates DocShare for the DocType with correct permissions"""
        frappe.set_user(self.test_user)
        form_generator = FormGenerator(team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Query DocShare for the DocType
        docshare = frappe.db.get_value(
            "DocShare",
            {
                "share_doctype": "DocType",
                "share_name": form_generator.doctype.name,
                "user": self.test_user,
            },
            ["read", "write", "share", "submit"],
            as_dict=True,
        )

        # Assertions
        self.assertIsNotNone(docshare, "DocShare should exist for DocType")
        self.assertEqual(docshare.read, 1, "DocShare should have read permission")
        self.assertEqual(docshare.write, 1, "DocShare should have write permission")
        self.assertEqual(docshare.share, 1, "DocShare should have share permission")
        self.assertEqual(docshare.submit, 0, "DocShare should not have submit permission")

    def test_generate_creates_form_docshare(self):
        """Test that generate() creates DocShare for the Form document with correct permissions"""
        frappe.set_user(self.test_user)
        form_generator = FormGenerator(team_id=self.test_team)

        # Call generate method
        form_generator.generate()

        # Query DocShare for the Form document
        docshare = frappe.db.get_value(
            "DocShare",
            {
                "share_doctype": "Form",
                "share_name": form_generator.form_document.name,
                "user": self.test_user,
            },
            ["read", "write", "share", "submit"],
            as_dict=True,
        )

        # Assertions
        self.assertIsNotNone(docshare, "DocShare should exist for Form document")
        self.assertEqual(docshare.read, 1, "DocShare should have read permission")
        self.assertEqual(docshare.write, 1, "DocShare should have write permission")
        self.assertEqual(docshare.share, 1, "DocShare should have share permission")
        self.assertEqual(docshare.submit, 0, "DocShare should not have submit permission")

    def test_status_field_is_added_custom_doctype(self):
        """Test that status field is added to custom doctype"""
        from forms_pro.utils.form_generator import SUBMISSION_STATUS_FIELDOPTIONS

        frappe.set_user(self.test_user)
        form_generator = FormGenerator(team_id=self.test_team)
        form_generator.generate()

        frappe.set_user("Administrator")
        # Assertions
        self.assertIsNotNone(form_generator.doctype.fields)
        status_field = next(
            field
            for field in form_generator.doctype.fields
            if field.fieldname == SUBMISSION_STATUS_FIELDOPTIONS["fieldname"]
        )
        assert status_field is not None, "Status field should be added to doctype"
        self.assertEqual(status_field.label, SUBMISSION_STATUS_FIELDOPTIONS["label"])
        self.assertEqual(status_field.fieldname, SUBMISSION_STATUS_FIELDOPTIONS["fieldname"])
        self.assertEqual(status_field.fieldtype, SUBMISSION_STATUS_FIELDOPTIONS["fieldtype"])
        self.assertEqual(status_field.options, SUBMISSION_STATUS_FIELDOPTIONS["options"])
        self.assertEqual(status_field.default, SUBMISSION_STATUS_FIELDOPTIONS["default"])
        self.assertEqual(status_field.read_only, SUBMISSION_STATUS_FIELDOPTIONS["read_only"])
        self.assertEqual(status_field.in_list_view, SUBMISSION_STATUS_FIELDOPTIONS["in_list_view"])

    def test_linked_form_field_is_added_custom_doctype(self):
        """Test that linked form field is added to custom doctype"""
        from forms_pro.utils.form_generator import LINKED_FORM_FIELDOPTIONS

        frappe.set_user(self.test_user)
        form_generator = FormGenerator(team_id=self.test_team)
        form_generator.generate()

        frappe.set_user("Administrator")
        self.assertIsNotNone(form_generator.doctype.fields)
        linked_form_field = next(
            field
            for field in form_generator.doctype.fields
            if field.fieldname == LINKED_FORM_FIELDOPTIONS["fieldname"]
        )
        assert linked_form_field is not None, "Linked form field should be added to doctype"
        self.assertEqual(linked_form_field.label, LINKED_FORM_FIELDOPTIONS["label"])
        self.assertEqual(linked_form_field.fieldname, LINKED_FORM_FIELDOPTIONS["fieldname"])
        self.assertEqual(linked_form_field.fieldtype, LINKED_FORM_FIELDOPTIONS["fieldtype"])
        self.assertEqual(linked_form_field.options, LINKED_FORM_FIELDOPTIONS["options"])
        self.assertEqual(linked_form_field.read_only, LINKED_FORM_FIELDOPTIONS["read_only"])

    def test_status_field_is_added_core_doctype(self):
        """Test that status field is added to core doctype as a custom field"""
        from forms_pro.utils.form_generator import SUBMISSION_STATUS_FIELDOPTIONS

        test_doctype = frappe.new_doc("DocType")
        test_doctype.name = "Test Status Field Doctype" + frappe.utils.random_string(8)
        test_doctype.module = "User Forms"
        test_doctype.custom = False
        test_doctype.insert(ignore_permissions=True)

        frappe.set_user(self.test_user)
        form_generator = FormGenerator(linked_doctype=test_doctype.name, team_id=self.test_team)
        form_generator.generate()

        # Assertions
        frappe.set_user("Administrator")
        self.assertIsNotNone(form_generator.doctype.fields)
        status_field = next(
            field
            for field in form_generator.doctype.fields
            if field.fieldname == SUBMISSION_STATUS_FIELDOPTIONS["fieldname"]
        )
        assert status_field is not None, "Status field should be added to doctype"

        custom_field_id = frappe.db.exists(
            "Custom Field",
            {"dt": test_doctype.name, "fieldname": SUBMISSION_STATUS_FIELDOPTIONS["fieldname"]},
        )
        self.assertIsNotNone(custom_field_id, "Custom field should be created for doctype")

        custom_field = frappe.get_doc("Custom Field", custom_field_id)

        self.assertEqual(custom_field.dt, test_doctype.name)
        self.assertEqual(custom_field.fieldname, SUBMISSION_STATUS_FIELDOPTIONS["fieldname"])
        self.assertEqual(custom_field.fieldtype, SUBMISSION_STATUS_FIELDOPTIONS["fieldtype"])
        self.assertEqual(custom_field.options, SUBMISSION_STATUS_FIELDOPTIONS["options"])
        self.assertEqual(custom_field.default, SUBMISSION_STATUS_FIELDOPTIONS["default"])
        self.assertEqual(custom_field.read_only, SUBMISSION_STATUS_FIELDOPTIONS["read_only"])
        self.assertEqual(custom_field.in_list_view, SUBMISSION_STATUS_FIELDOPTIONS["in_list_view"])

    def test_linked_form_field_is_added_core_doctype(self):
        """Test that linked form field is added to core doctype as a custom field"""
        from forms_pro.utils.form_generator import LINKED_FORM_FIELDOPTIONS

        test_doctype = frappe.new_doc("DocType")
        test_doctype.name = "Test Linked Form Doctype" + frappe.utils.random_string(8)
        test_doctype.module = "User Forms"
        test_doctype.custom = False
        test_doctype.insert(ignore_permissions=True)

        frappe.set_user(self.test_user)
        form_generator = FormGenerator(linked_doctype=test_doctype.name, team_id=self.test_team)
        form_generator.generate()

        # Assertions
        frappe.set_user("Administrator")
        self.assertIsNotNone(form_generator.doctype.fields)
        linked_form_field = next(
            field
            for field in form_generator.doctype.fields
            if field.fieldname == LINKED_FORM_FIELDOPTIONS["fieldname"]
        )
        assert linked_form_field is not None, "Linked form field should be added to doctype"

        custom_field_id = frappe.db.exists(
            "Custom Field",
            {"dt": test_doctype.name, "fieldname": LINKED_FORM_FIELDOPTIONS["fieldname"]},
        )
        self.assertIsNotNone(custom_field_id, "Custom field should be created for doctype")

        custom_field = frappe.get_doc("Custom Field", custom_field_id)

        self.assertEqual(custom_field.dt, test_doctype.name)
        self.assertEqual(custom_field.fieldname, LINKED_FORM_FIELDOPTIONS["fieldname"])
        self.assertEqual(custom_field.fieldtype, LINKED_FORM_FIELDOPTIONS["fieldtype"])
        self.assertEqual(custom_field.options, LINKED_FORM_FIELDOPTIONS["options"])
        self.assertEqual(custom_field.read_only, LINKED_FORM_FIELDOPTIONS["read_only"])
