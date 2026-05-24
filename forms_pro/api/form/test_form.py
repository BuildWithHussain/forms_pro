import frappe
from frappe.share import add_docshare
from frappe.tests import IntegrationTestCase

from forms_pro.api.form import (
    add_form_access,
    get_form_for_edit,
    get_form_for_view,
    get_form_shared_with,
    remove_form_access,
    set_form_permission,
)
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


class TestGetFormSharedWith(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_admin_can_list_shares(self) -> None:
        result = get_form_shared_with(form_id=self.form.name)
        self.assertIsInstance(result, list)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_form_shared_with(form_id=self.form.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_form_shared_with(form_id="MISSING_FORM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestAddFormAccess(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()

    def test_admin_can_add_access(self) -> None:
        add_form_access(
            form_id=self.form.name,
            user=FORMS_PRO_TEST_USER,
            read=True,
        )
        self.assertTrue(
            frappe.db.exists(
                "DocShare",
                {"share_doctype": "Form", "share_name": self.form.name, "user": FORMS_PRO_TEST_USER},
            )
        )

    def test_raises_403_when_user_lacks_share(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                add_form_access(form_id=self.form.name, user="x@y.z", read=True)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            add_form_access(form_id="MISSING_FORM_XYZ", user=FORMS_PRO_TEST_USER, read=True)
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestRemoveFormAccess(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()
        add_docshare(
            doctype="Form",
            name=self.form.name,
            user=FORMS_PRO_TEST_USER,
            read=1,
            flags={"ignore_share_permission": True},
        )

    def test_admin_can_remove_access(self) -> None:
        remove_form_access(form_id=self.form.name, user_email=FORMS_PRO_TEST_USER)
        self.assertFalse(
            frappe.db.exists(
                "DocShare",
                {"share_doctype": "Form", "share_name": self.form.name, "user": FORMS_PRO_TEST_USER},
            )
        )

    def test_raises_403_when_user_lacks_write(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                remove_form_access(form_id=self.form.name, user_email=FORMS_PRO_TEST_USER)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            remove_form_access(form_id="MISSING_FORM_XYZ", user_email=FORMS_PRO_TEST_USER)
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestSetFormPermission(IntegrationTestCase):
    def setUp(self) -> None:
        self.form = FormFactory.create()
        add_docshare(
            doctype="Form",
            name=self.form.name,
            user=FORMS_PRO_TEST_USER,
            read=1,
            flags={"ignore_share_permission": True},
        )

    def test_admin_can_set_permission(self) -> None:
        set_form_permission(
            form_id=self.form.name,
            user=FORMS_PRO_TEST_USER,
            permission_to="write",
            value=True,
        )
        share = frappe.get_value(
            "DocShare",
            {"share_doctype": "Form", "share_name": self.form.name, "user": FORMS_PRO_TEST_USER},
            ["write"],
            as_dict=True,
        )
        self.assertEqual(share["write"], 1)

    def test_raises_403_when_user_lacks_share(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            with self.assertRaises(frappe.PermissionError) as ctx:
                set_form_permission(
                    form_id=self.form.name,
                    user=FORMS_PRO_TEST_USER,
                    permission_to="write",
                    value=True,
                )
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_form_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            set_form_permission(
                form_id="MISSING_FORM_XYZ",
                user=FORMS_PRO_TEST_USER,
                permission_to="write",
                value=True,
            )
        self.assertEqual(ctx.exception.http_status_code, 404)
