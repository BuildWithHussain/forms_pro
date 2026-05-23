import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.api.form import get_form_for_view
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
