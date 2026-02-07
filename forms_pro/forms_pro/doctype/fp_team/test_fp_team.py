# Copyright (c) 2025, harsh@buildwithhussain.com and Contributors
# See license.txt

import frappe
from frappe.defaults import get_user_default
from frappe.tests import IntegrationTestCase

from forms_pro.tests import FORMS_PRO_TEST_USER

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestFPTeam(IntegrationTestCase):
    """
    Integration tests for FPTeam.
    Use this class for testing interactions between multiple components.
    """

    def setUp(self):
        super().setUp()
        self.test_user = FORMS_PRO_TEST_USER

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def test_add_owner_to_team(self):
        """
        Test that after a user creates a team, that owner user is added to the team and the team is shared with the owner user
        """

        frappe.set_user(self.test_user)

        team = frappe.new_doc("FP Team")
        team.team_name = "Test Team"
        team.insert()
        team.reload()

        frappe.set_user("Administrator")

        # Check that the user is added to the team
        self.assertTrue(team.is_team_member(self.test_user))

        # Check that the user is added to the team
        self.assertIsNotNone(
            frappe.db.exists(
                "FP Team Member",
                {
                    "parent": team.name,
                    "parentfield": "users",
                    "parenttype": "FP Team",
                    "user": self.test_user,
                },
            )
        )

        # Check that the user is added to the team's docshare
        self.assertTrue(
            frappe.db.exists(
                "DocShare",
                {
                    "share_doctype": "FP Team",
                    "share_name": team.name,
                    "user": self.test_user,
                    "read": 1,
                    "write": 1,
                    "share": 1,
                },
            )
        )

        # Check that the user's current team is set to the team
        self.assertEqual(get_user_default("current_team", self.test_user), team.name)
