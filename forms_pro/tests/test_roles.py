# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.roles import FORMS_PRO_ROLE
from forms_pro.tests.factories import UserFactory
from forms_pro.utils.teams import get_user_teams


class TestRoles(IntegrationTestCase):
    def setUp(self):
        super().setUp()

    def test_roles(self):
        user = UserFactory.create()
        roles = frappe.get_roles(user.name)
        self.assertNotIn(FORMS_PRO_ROLE, roles)
        self.assertEqual(len(get_user_teams(user.name)), 0)

        # Role assignment post-insert is intentional here: this test specifically
        # exercises the on_update hook that fires when a role is added after creation.
        user.append_roles(FORMS_PRO_ROLE)
        user.save()
        roles = frappe.get_roles(user.name)
        self.assertIn(FORMS_PRO_ROLE, roles)

        team = get_user_teams(user.name)
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].team_name, f"{user.first_name}'s Team")
