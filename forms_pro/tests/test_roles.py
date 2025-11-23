import frappe
from faker import Faker
from frappe.core.doctype.user.user import User
from frappe.tests import IntegrationTestCase

from forms_pro.roles import FORMS_PRO_ROLE
from forms_pro.utils.teams import get_user_teams


class TestRoles(IntegrationTestCase):
    def setUp(self):
        super().setUp()

    def test_roles(self):
        fake = Faker()
        user: User = frappe.get_doc(
            {
                "doctype": "User",
                "email": fake.email(),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
            }
        )
        user.insert()
        roles = frappe.get_roles(user.name)
        self.assertNotIn(FORMS_PRO_ROLE, roles)
        self.assertEqual(len(get_user_teams(user.name)), 0)

        user.append_roles(FORMS_PRO_ROLE)
        user.save()
        roles = frappe.get_roles(user.name)
        self.assertIn(FORMS_PRO_ROLE, roles)

        team = get_user_teams(user.name)
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].team_name, f"{user.first_name}'s Team")
