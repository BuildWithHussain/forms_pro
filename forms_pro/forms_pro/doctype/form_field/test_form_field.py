# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase

from forms_pro.forms_pro.doctype.form_field.form_field import FORM_TO_FRAPPE_FIELDTYPE


def _build_field(
    fieldtype: str, label: str = "Test Field", fieldname: str = "test_field", options: str | None = None
):
    """Build an in-memory FormField document without inserting."""
    doc = frappe.get_doc(
        {
            "doctype": "Form Field",
            "fieldtype": fieldtype,
            "label": label,
            "fieldname": fieldname,
            "options": options,
        }
    )
    return doc


class TestFormFieldGetOptions(IntegrationTestCase):
    def test_heading_1_returns_h1_tag_wrapping_label(self):
        field = _build_field("Heading 1", label="Introduction")
        self.assertEqual(field.get_options(), "<h1>Introduction</h1>")

    def test_heading_2_returns_h2_tag_wrapping_label(self):
        field = _build_field("Heading 2", label="Section A")
        self.assertEqual(field.get_options(), "<h2>Section A</h2>")

    def test_heading_3_returns_h3_tag_wrapping_label(self):
        field = _build_field("Heading 3", label="Subsection")
        self.assertEqual(field.get_options(), "<h3>Subsection</h3>")

    def test_non_heading_returns_options_unchanged(self):
        field = _build_field("Select", label="Color", options="Red\nBlue\nGreen")
        self.assertEqual(field.get_options(), "Red\nBlue\nGreen")

    def test_non_heading_with_no_options_returns_none(self):
        field = _build_field("Data", label="Name")
        self.assertIsNone(field.get_options())


class TestFormFieldToFrappeField(IntegrationTestCase):
    def test_heading_1_maps_to_html_fieldtype(self):
        field = _build_field("Heading 1", label="My Heading", fieldname="my_heading")
        result = field.to_frappe_field
        self.assertEqual(result["fieldtype"], "HTML")

    def test_heading_2_maps_to_html_fieldtype(self):
        field = _build_field("Heading 2", label="Sub Heading", fieldname="sub_heading")
        self.assertEqual(field.to_frappe_field["fieldtype"], "HTML")

    def test_heading_3_maps_to_html_fieldtype(self):
        field = _build_field("Heading 3", label="Minor Heading", fieldname="minor_heading")
        self.assertEqual(field.to_frappe_field["fieldtype"], "HTML")

    def test_heading_options_contains_html_tag(self):
        field = _build_field("Heading 1", label="My Title", fieldname="my_title")
        result = field.to_frappe_field
        self.assertIn("<h1>", result["options"])
        self.assertIn("My Title", result["options"])

    def test_data_field_maps_to_data_frappe_fieldtype(self):
        field = _build_field("Data", label="Name", fieldname="name_field")
        self.assertEqual(field.to_frappe_field["fieldtype"], "Data")

    def test_form_to_frappe_fieldtype_has_all_heading_levels(self):
        for fieldtype in ("Heading 1", "Heading 2", "Heading 3"):
            with self.subTest(fieldtype=fieldtype):
                self.assertIn(fieldtype, FORM_TO_FRAPPE_FIELDTYPE)
                self.assertEqual(FORM_TO_FRAPPE_FIELDTYPE[fieldtype]["fieldtype"], "HTML")


class TestLayoutFieldsNotSyncedToDoctype(IntegrationTestCase):
    """row_index, column_index, cell_index are layout-only and must never appear in to_frappe_field."""

    def test_row_index_excluded_from_frappe_field(self):
        field = _build_field("Data", label="Name", fieldname="name_field")
        field.row_index = 3
        self.assertNotIn("row_index", field.to_frappe_field)

    def test_column_index_excluded_from_frappe_field(self):
        field = _build_field("Data", label="Name", fieldname="name_field")
        field.column_index = 2
        self.assertNotIn("column_index", field.to_frappe_field)

    def test_cell_index_excluded_from_frappe_field(self):
        field = _build_field("Data", label="Name", fieldname="name_field")
        field.cell_index = 4
        self.assertNotIn("cell_index", field.to_frappe_field)

    def test_layout_fields_excluded_for_all_fieldtypes(self):
        for fieldtype in FORM_TO_FRAPPE_FIELDTYPE:
            with self.subTest(fieldtype=fieldtype):
                field = _build_field(fieldtype, label="Test", fieldname="test_f")
                field.row_index = 1
                field.column_index = 1
                field.cell_index = 1
                result = field.to_frappe_field
                self.assertNotIn("row_index", result)
                self.assertNotIn("column_index", result)
                self.assertNotIn("cell_index", result)
