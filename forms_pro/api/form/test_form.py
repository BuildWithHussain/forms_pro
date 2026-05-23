import frappe
from frappe.share import add_docshare
from frappe.tests import IntegrationTestCase

from forms_pro.api.form import get_form_for_edit, get_form_for_view
from forms_pro.tests import FORMS_PRO_TEST_USER
from forms_pro.tests.factories.form_factory import FormFactory


class TestGetFormForView(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_returns_form_when_user_has_read(self) -> None:
        result = get_form_for_view(form_id=self.form.name)
        self.assertEqual(result["name"], self.form.name)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_form_for_view(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_form_for_view(form_id="MISSING_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestGetFormForEdit(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_returns_form_when_user_has_write(self) -> None:
        result = get_form_for_edit(form_id=self.form.name)
        self.assertEqual(result["name"], self.form.name)

    def test_raises_403_when_user_has_read_but_not_write(self) -> None:
        # Share read-only with the low-privilege user, then assert write is denied.
        add_docshare(
            doctype="Form",
            name=self.form.name,
            user=FORMS_PRO_TEST_USER,
            read=1,
            write=0,
            share=0,
            flags={"ignore_share_permission": True},
        )
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_form_for_edit(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_form_for_edit(form_id="MISSING_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)
