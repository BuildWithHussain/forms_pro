import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.tests import FORMS_PRO_TEST_USER
from forms_pro.tests.factories.form_factory import FormFactory
from forms_pro.utils.permissions import require_permission


class TestRequirePermission(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_allows_when_permission_granted(self) -> None:
        @require_permission("Form", "read", param="form_id")
        def fn(form_id: str) -> str:
            return form_id

        self.assertEqual(fn(form_id=self.form.name), self.form.name)

    def test_raises_permission_error_when_denied(self) -> None:
        @require_permission("Form", "write", param="form_id")
        def fn(form_id: str) -> str:
            return form_id

        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                fn(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_does_not_exist_when_doc_missing(self) -> None:
        @require_permission("Form", "read", param="form_id")
        def fn(form_id: str) -> str:
            return form_id

        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            fn(form_id="NON_EXISTENT_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)

    def test_create_ptype_skips_existence_and_docname(self) -> None:
        @require_permission("Form", "create")
        def fn() -> str:
            return "ok"

        self.assertEqual(fn(), "ok")

    def test_param_kwarg_routing(self) -> None:
        @require_permission("Form", "read", param="my_id")
        def fn(my_id: str) -> str:
            return my_id

        self.assertEqual(fn(my_id=self.form.name), self.form.name)
