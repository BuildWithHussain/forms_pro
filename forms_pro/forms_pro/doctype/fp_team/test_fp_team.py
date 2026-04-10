# Copyright (c) 2025, harsh@buildwithhussain.com and Contributors
# See license.txt

import frappe
from frappe.defaults import get_user_default
from frappe.tests import IntegrationTestCase

from forms_pro.tests.factories import FPTeamFactory, UserFactory

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
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def test_add_owner_to_team(self):
        """
        Test that after a user creates a team, that owner user is added to the team and the team is shared with the owner user
        """

        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)

        team = FPTeamFactory.create()
        team.reload()

        frappe.set_user("Administrator")

        # Check that the owner is added to the team
        self.assertTrue(team.is_team_member(owner.name))

        # Check that the FP Team Member row exists
        self.assertIsNotNone(
            frappe.db.exists(
                "FP Team Member",
                {
                    "parent": team.name,
                    "parentfield": "users",
                    "parenttype": "FP Team",
                    "user": owner.name,
                },
            )
        )

        # Check that the team is shared with the owner
        self.assertTrue(
            frappe.db.exists(
                "DocShare",
                {
                    "share_doctype": "FP Team",
                    "share_name": team.name,
                    "user": owner.name,
                    "read": 1,
                    "write": 1,
                    "share": 1,
                },
            )
        )

        # Check that the owner's current team is set to this team
        self.assertEqual(get_user_default("current_team", owner.name), team.name)
