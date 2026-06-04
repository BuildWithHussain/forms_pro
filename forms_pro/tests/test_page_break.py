import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.tests.factories.form_factory import FormFactory


class TestPageBreakIntegration(IntegrationTestCase):
    def test_form_with_page_break_saves(self):
        form = FormFactory.create()
        form.append(
            "fields",
            {
                "label": "Your Name",
                "fieldname": "your_name",
                "fieldtype": "Data",
                "reqd": 0,
                "row_index": 0,
                "column_index": 0,
                "cell_index": 0,
            },
        )
        form.append(
            "fields",
            {
                "label": "Step 2",
                "fieldname": "step_2",
                "fieldtype": "Page Break",
                "reqd": 0,
                "row_index": 1,
                "column_index": 0,
                "cell_index": 0,
            },
        )
        form.append(
            "fields",
            {
                "label": "Your Email",
                "fieldname": "your_email",
                "fieldtype": "Email",
                "reqd": 0,
                "row_index": 2,
                "column_index": 0,
                "cell_index": 0,
            },
        )
        form.save()

        form.reload()
        fieldtypes = [f.fieldtype for f in form.fields]
        self.assertIn("Page Break", fieldtypes)

    def test_page_break_syncs_as_html_to_linked_doctype(self):
        form = FormFactory.create()
        form.append(
            "fields",
            {
                "label": "Step 2",
                "fieldname": "step_2",
                "fieldtype": "Page Break",
                "reqd": 0,
                "row_index": 0,
                "column_index": 0,
                "cell_index": 0,
            },
        )
        form.save()

        doctype_doc = frappe.get_doc("DocType", form.linked_doctype)
        synced = {f.fieldname: f for f in doctype_doc.fields}
        self.assertIn("step_2", synced)
        self.assertEqual(synced["step_2"].fieldtype, "HTML")
        self.assertEqual(synced["step_2"].options, "<hr>")
