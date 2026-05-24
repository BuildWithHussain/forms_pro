# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

from unittest.mock import patch

import frappe
from faker import Faker
from frappe.model.document import Document
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase

from forms_pro.api.team import add_member_to_team_via_invitation, invite_team_members
from forms_pro.overrides.invitations import after_accept, after_insert
from forms_pro.roles import FORMS_PRO_ROLE
from forms_pro.tests.factories import FPTeamFactory, UserFactory
from forms_pro.tests.factories.user_invitation_factory import UserInvitationFactory

fake = Faker()


class _StubRole:
    def __init__(self, role: str):
        self.role = role


class _StubInvitationDoc:
    """Minimal doc-like object for testing after_insert skip logic without DB."""

    def __init__(self, app_name: str, redirect_to_path: str, roles: list):
        self.app_name = app_name
        self.redirect_to_path = redirect_to_path
        self.roles = roles
        self.name = "STUB-INV-001"

    def save(self, ignore_permissions: bool = False):
        pass


class TestTeamInvitations(IntegrationTestCase):
    """Tests for team invitation flow: invite_team_members, after_insert hook, add_member_to_team_via_invitation."""

    def setUp(self):
        super().setUp()
        self.sendmail_patcher = patch("frappe.sendmail")
        mock_sendmail = self.sendmail_patcher.start()
        mock_sendmail.return_value.message = ""
        frappe.set_user("Administrator")

    def tearDown(self):
        self.sendmail_patcher.stop()
        frappe.set_user("Administrator")
        super().tearDown()

    def _make_accepted_invitation(self, invitee: Document, owner: Document) -> Document:
        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": invitee.name,
                "app_name": "forms_pro",
                "redirect_to_path": "/forms",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner.name,
            }
        )
        inv_doc.insert(ignore_permissions=True)
        inv_doc.db_set("status", "Accepted")
        inv_doc.db_set("user", invitee.name)
        return inv_doc

    def _get_team_memberships(self, user: Document) -> list:
        return frappe.get_all("FP Team Member", filters={"user": user.name})

    # --- invite_team_members ---

    def test_invite_requires_permission(self):
        """User without write permission on team cannot invite members."""
        owner = UserFactory.create("with_forms_pro_role")
        other = UserFactory.create()
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()

        frappe.set_user(other.name)
        with self.assertRaises(frappe.PermissionError) as ctx:
            invite_team_members(team_id=team.name, emails=[other.email])
        self.assertIn("permission", str(ctx.exception).lower())

    def test_invite_creates_invitation_with_redirect(self):
        """Inviting creates a User Invitation whose redirect contains team_id and invite_id."""
        owner = UserFactory.create("with_forms_pro_role")
        invitee_email = fake.email()

        frappe.set_user(owner.name)
        team = FPTeamFactory.create()

        invite_team_members(team_id=team.name, emails=[invitee_email])

        invitations = frappe.get_all(
            "User Invitation",
            filters={"email": invitee_email, "app_name": "forms_pro"},
            fields=["name", "redirect_to_path"],
        )
        self.assertEqual(len(invitations), 1)
        inv = invitations[0]
        self.assertIn(team.name, inv.redirect_to_path)
        self.assertIn("add_member_to_team_via_invitation", inv.redirect_to_path)
        self.assertIn(f"invite_id={inv.name}", inv.redirect_to_path)

    # --- after_insert hook ---

    def test_after_insert_adds_invite_id_to_redirect(self):
        """after_insert hook rewrites redirect_to_path to include invite_id."""
        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        invite_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            team=team,
            email=fake.email(),
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
        )
        self.assertIn(team.name, invite_doc.redirect_to_path)
        self.assertIn(f"invite_id={invite_doc.name}", invite_doc.redirect_to_path)
        self.assertIn("add_member_to_team_via_invitation", invite_doc.redirect_to_path)

    def test_after_insert_skips_non_forms_pro_app(self):
        """after_insert does not modify redirect when app_name is not forms_pro."""
        original_path = "/some/path?team_id=abc"
        invite_doc = UserInvitationFactory.create(
            app_name="frappe",
            redirect_to_path=original_path,
            roles=[{"role": "System Manager"}],
            invited_by="Administrator",
        )
        after_insert(invite_doc, "after_insert")
        self.assertEqual(invite_doc.redirect_to_path, original_path)

    def test_after_insert_raises_when_roles_do_not_include_forms_pro_user(self):
        """after_insert raises when roles do not include Forms Pro User for forms_pro app"""
        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)

        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        original_path = f"/api/v2/method/some.method?team_id={team.name}"
        role = "System Manager"

        with self.assertRaises(frappe.ValidationError) as ctx:
            UserInvitationFactory.create(
                app_name="forms_pro",
                redirect_to_path=original_path,
                roles=[{"role": role}],
            )
        self.assertIn(f"{role} is not an allowed role for forms_pro", str(ctx.exception))

    # --- add_member_to_team_via_invitation ---

    def test_add_member_to_team_via_invitation_raises_when_invitation_is_pending(self):
        """Raises PermissionError when invitation status is not Accepted."""
        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        inv_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            team=team,
            email=fake.email(),
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
            status="Pending",
        )

        with self.assertRaises(frappe.PermissionError) as ctx:
            add_member_to_team_via_invitation(team_id=team.name, invite_id=inv_doc.name)
        self.assertIn("Invitation not accepted", str(ctx.exception))

    def test_add_member_to_team_via_invitation_raises_when_user_not_found(self):
        """Raises PermissionError when the invited email has no User record."""
        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        inv_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            team=team,
            email=fake.email(),
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
        )
        inv_doc.status = "Accepted"
        inv_doc.save(ignore_permissions=True)

        with self.assertRaises(frappe.PermissionError) as ctx:
            add_member_to_team_via_invitation(team_id=team.name, invite_id=inv_doc.name)
        self.assertIn("User not found", str(ctx.exception))

    def test_add_member_to_team_via_invitation_adds_user_to_team_and_redirects(self):
        """Successfully adds user to team and sets redirect response to /forms."""
        owner = UserFactory.create("with_forms_pro_role")
        invitee = UserFactory.create()
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        inv_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            team=team,
            email=invitee.email,
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
        )
        inv_doc.status = "Accepted"
        inv_doc.save(ignore_permissions=True)

        add_member_to_team_via_invitation(team_id=team.name, invite_id=inv_doc.name)

        team_doc = frappe.get_doc("FP Team", team.name)
        self.assertIn(invitee.name, [row.user for row in team_doc.users])
        self.assertEqual(frappe.local.response.get("type"), "redirect")
        self.assertEqual(frappe.local.response.get("location"), "/forms")

    # --- after_accept hook ---

    def test_after_accept_adds_user_to_inviting_team(self):
        """after_accept adds the invited user to the team and updates redirect to /forms."""
        owner = UserFactory.create("with_forms_pro_role")
        invitee = UserFactory.create()
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        inv_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            team=team,
            email=invitee.email,
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
        )
        inv_doc.status = "Accepted"
        inv_doc.save(ignore_permissions=True)

        after_accept(invitation=inv_doc, user=invitee, user_inserted=True)

        team_doc = frappe.get_doc("FP Team", team.name)
        self.assertIn(invitee.name, [row.user for row in team_doc.users])
        self.assertEqual(inv_doc.redirect_to_path, "/forms")

    def test_after_accept_skips_when_no_team_id(self):
        """after_accept is a no-op when redirect_to_path has no team_id."""
        owner = UserFactory.create("with_forms_pro_role")
        invitee = UserFactory.create()

        inv_doc = UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            email=invitee.email,
            redirect_to_path="/forms",
        )
        inv_doc.status = "Accepted"
        inv_doc.save(ignore_permissions=True)

        after_accept(invitation=inv_doc, user=invitee, user_inserted=True)

        self.assertEqual(inv_doc.redirect_to_path, "/forms")
        self.assertEqual(self._get_team_memberships(invitee), [])

    # --- default team creation guard (bug fix) ---

    def test_no_default_team_created_for_invited_user(self):
        """
        When a user receives the Forms Pro role but has a pending invitation,
        the role-change hook must NOT create a default team — the invitation
        redirect will place them in the correct inviting team instead.
        """
        invitee = UserFactory.create()
        owner = UserFactory.create("with_forms_pro_role")
        frappe.set_user(owner.name)
        team = FPTeamFactory.create()
        frappe.set_user("Administrator")

        # Simulate a pending invitation (exists before the user accepts)
        UserInvitationFactory.create(
            "to_forms_pro_app",
            invited_by=owner.name,
            email=invitee.email,
            redirect_to_path=f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team.name}",
            status="Pending",
        )

        # Assigning the Forms Pro role is what Frappe does on invitation acceptance;
        # the hook must skip default team creation here.
        invitee.append_roles(FORMS_PRO_ROLE)
        invitee.save(ignore_permissions=True)

        # There should be no team memberships for the invited user
        # because the role change hook will not create a default team.
        # Team will be created by the invitation redirect.

        self.assertEqual(
            self._get_team_memberships(invitee),
            [],
            "A default team must not be created for an invited user",
        )
