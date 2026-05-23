import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.api.submission import get_all_submissions, get_user_submissions
from forms_pro.tests import FORMS_PRO_TEST_USER
from forms_pro.tests.factories.form_factory import FormFactory


class TestGetUserSubmissions(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_admin_can_list_user_submissions(self) -> None:
        result = get_user_submissions(form_id=self.form.name)
        self.assertIsInstance(result, list)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_user_submissions(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_user_submissions(form_id="MISSING_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestGetAllSubmissions(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_admin_can_list_all_submissions(self) -> None:
        result = get_all_submissions(form_id=self.form.name)
        self.assertIsInstance(result, list)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_all_submissions(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_all_submissions(form_id="MISSING_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)
