import frappe
from frappe.core.doctype.user.user import User

from forms_pro.roles import FORMS_PRO_ROLE
from forms_pro.tests import FORMS_PRO_TEST_USER


def after_install():
    create_user_forms_module()


def create_user_forms_module():
    if frappe.db.exists("Module Def", "User Forms"):
        return

    module = frappe.new_doc("Module Def")
    module.module_name = "User Forms"
    module.app_name = "Forms Pro"
    module.insert(ignore_permissions=True)


def before_tests():
    give_admin_forms_pro_role()
    create_test_user()


def give_admin_forms_pro_role():
    admin = frappe.get_doc("User", "Administrator")
    admin.append("roles", {"role": FORMS_PRO_ROLE})
    admin.save()


def create_test_user():
    if frappe.db.exists("User", FORMS_PRO_TEST_USER):
        return

    user: User = frappe.new_doc("User")
    user.email = FORMS_PRO_TEST_USER
    user.first_name = "Test"
    user.last_name = "Forms Pro User"
    user.insert(ignore_permissions=True)
    user.append("roles", {"role": FORMS_PRO_ROLE})
    user.save(ignore_permissions=True)
