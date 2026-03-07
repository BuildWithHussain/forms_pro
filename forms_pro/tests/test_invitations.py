# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

from unittest.mock import patch

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from forms_pro.api.team import add_member_to_team_via_invitation, invite_team_members
from forms_pro.overrides.invitations import after_accept, after_insert
from forms_pro.roles import FORMS_PRO_ROLE


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
        self.sendmail_patcher.start()
        self.fake = Faker()
        self.teams_created = []
        self.users_created = []
        frappe.set_user("Administrator")

    def tearDown(self):
        patcher = getattr(self, "sendmail_patcher", None)
        if patcher is not None:
            patcher.stop()
        frappe.set_user("Administrator")
        for team_id in self.teams_created:
            if frappe.db.exists("FP Team", team_id):
                frappe.delete_doc("FP Team", team_id, force=True, ignore_permissions=True)
        for email in self.users_created:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, force=True, ignore_permissions=True)
        frappe.db.delete("User Invitation", {"app_name": "forms_pro"})
        frappe.db.commit()
        super().tearDown()

    def _create_user(self, email: str | None = None, with_forms_pro_role: bool = True) -> str:
        email = email or self.fake.email()
        if frappe.db.exists("User", email):
            return email
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
            }
        )
        user.insert(ignore_permissions=True)
        if with_forms_pro_role:
            user.append_roles(FORMS_PRO_ROLE)
            user.save(ignore_permissions=True)
        self.users_created.append(email)
        return email

    def _create_team(self, owner: str, team_name: str | None = None) -> str:
        frappe.set_user(owner)
        team = frappe.get_doc(
            {
                "doctype": "FP Team",
                "team_name": team_name or f"{self.fake.word()} Team",
            }
        )
        team.insert()
        self.teams_created.append(team.name)
        frappe.set_user("Administrator")
        return team.name

    def _make_accepted_invitation(self, invitee_email: str, owner: str) -> object:
        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": invitee_email,
                "app_name": "forms_pro",
                "redirect_to_path": "/forms",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
            }
        )
        inv_doc.insert(ignore_permissions=True)
        inv_doc.db_set("status", "Accepted")
        inv_doc.db_set("user", invitee_email)
        frappe.db.commit()
        return inv_doc

    def _get_team_memberships(self, email: str) -> list:
        return frappe.get_all("FP Team Member", filters={"user": email})

    # --- invite_team_members ---

    def test_invite_requires_permission(self):
        """User without read permission on team cannot invite members."""
        owner = self._create_user()
        other = self._create_user(with_forms_pro_role=False)
        team_id = self._create_team(owner)

        frappe.set_user(other)
        with self.assertRaises(frappe.PermissionError) as ctx:
            invite_team_members(team_id=team_id, emails=[self.fake.email()])
        self.assertIn("permission", str(ctx.exception).lower())

    def test_invite_creates_invitation_with_redirect(self):
        """Inviting creates a User Invitation whose redirect contains team_id and invite_id."""
        owner = self._create_user()
        invitee_email = self.fake.email()
        team_id = self._create_team(owner)

        frappe.set_user(owner)
        invite_team_members(team_id=team_id, emails=[invitee_email])
        frappe.db.commit()

        invitations = frappe.get_all(
            "User Invitation",
            filters={"email": invitee_email, "app_name": "forms_pro"},
            fields=["name", "redirect_to_path"],
        )
        self.assertEqual(len(invitations), 1)
        inv = invitations[0]
        self.assertIn(team_id, inv.redirect_to_path)
        self.assertIn("add_member_to_team_via_invitation", inv.redirect_to_path)
        self.assertIn(f"invite_id={inv.name}", inv.redirect_to_path)

    # --- after_insert hook ---

    def test_after_insert_adds_invite_id_to_redirect(self):
        """after_insert hook rewrites redirect_to_path to include invite_id."""
        team_id = self._create_team(self._create_user())
        doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": self.fake.email(),
                "app_name": "forms_pro",
                "redirect_to_path": f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team_id}",
                "roles": [{"role": FORMS_PRO_ROLE}],
            }
        )
        doc.insert(ignore_permissions=True)
        doc.reload()
        self.assertIn(team_id, doc.redirect_to_path)
        self.assertIn(f"invite_id={doc.name}", doc.redirect_to_path)
        self.assertIn("add_member_to_team_via_invitation", doc.redirect_to_path)
        frappe.delete_doc("User Invitation", doc.name, force=True)

    def test_after_insert_skips_non_forms_pro_app(self):
        """after_insert does not modify redirect when app_name is not forms_pro."""
        original_path = "/some/path?team_id=abc"
        doc = _StubInvitationDoc(
            app_name="other_app", redirect_to_path=original_path, roles=[_StubRole(FORMS_PRO_ROLE)]
        )
        after_insert(doc, "after_insert")
        self.assertEqual(doc.redirect_to_path, original_path)

    def test_after_insert_skips_wrong_roles(self):
        """after_insert does not modify redirect when roles do not include Forms Pro User."""
        team_id = self._create_team(self._create_user())
        original_path = f"/api/v2/method/some.method?team_id={team_id}"
        doc = _StubInvitationDoc(
            app_name="forms_pro", redirect_to_path=original_path, roles=[_StubRole("System Manager")]
        )
        after_insert(doc, "after_insert")
        self.assertEqual(doc.redirect_to_path, original_path)

    # --- add_member_to_team_via_invitation ---

    def test_add_member_raises_when_invitation_not_accepted(self):
        """Raises PermissionError when invitation status is not Accepted."""
        owner = self._create_user()
        team_id = self._create_team(owner)
        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": self.fake.email(),
                "app_name": "forms_pro",
                "redirect_to_path": "/forms",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
                "status": "Pending",
            }
        )
        inv_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        with self.assertRaises(frappe.PermissionError) as ctx:
            add_member_to_team_via_invitation(team_id=team_id, invite_id=inv_doc.name)
        self.assertIn("Invitation not accepted", str(ctx.exception))

    def test_add_member_raises_when_user_not_found(self):
        """Raises PermissionError when the invited email has no User record."""
        owner = self._create_user()
        team_id = self._create_team(owner)
        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": self.fake.email(),
                "app_name": "forms_pro",
                "redirect_to_path": "/forms",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
            }
        )
        inv_doc.insert(ignore_permissions=True)
        inv_doc.db_set("status", "Accepted")
        frappe.db.commit()

        with self.assertRaises(frappe.PermissionError) as ctx:
            add_member_to_team_via_invitation(team_id=team_id, invite_id=inv_doc.name)
        self.assertIn("User not found", str(ctx.exception))

    def test_add_member_adds_user_to_team_and_redirects(self):
        """Successfully adds user to team and sets redirect response to /forms."""
        owner = self._create_user()
        invitee_email = self._create_user(with_forms_pro_role=False)
        team_id = self._create_team(owner)
        inv_doc = self._make_accepted_invitation(invitee_email, owner)

        add_member_to_team_via_invitation(team_id=team_id, invite_id=inv_doc.name)

        team = frappe.get_doc("FP Team", team_id)
        self.assertIn(invitee_email, [row.user for row in team.users])
        self.assertEqual(frappe.local.response.get("type"), "redirect")
        self.assertEqual(frappe.local.response.get("location"), "/forms")

    # --- after_accept hook ---

    def test_after_accept_adds_user_to_inviting_team(self):
        """after_accept adds the invited user to the team and updates redirect to /forms."""
        owner = self._create_user()
        invitee_email = self._create_user(with_forms_pro_role=False)
        team_id = self._create_team(owner)

        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": invitee_email,
                "app_name": "forms_pro",
                "redirect_to_path": f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team_id}&invite_id=TEST-001",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
            }
        )
        inv_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        invitee_user = frappe.get_doc("User", invitee_email)
        after_accept(invitation=inv_doc, user=invitee_user, user_inserted=True)

        team = frappe.get_doc("FP Team", team_id)
        self.assertIn(invitee_email, [row.user for row in team.users])
        self.assertEqual(inv_doc.redirect_to_path, "/forms")
        frappe.delete_doc("User Invitation", inv_doc.name, force=True)

    def test_after_accept_skips_when_no_team_id(self):
        """after_accept is a no-op when redirect_to_path has no team_id."""
        owner = self._create_user()
        invitee_email = self._create_user(with_forms_pro_role=False)
        inv_doc = frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": invitee_email,
                "app_name": "forms_pro",
                "redirect_to_path": "/forms",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
            }
        )
        inv_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        invitee_user = frappe.get_doc("User", invitee_email)
        after_accept(invitation=inv_doc, user=invitee_user, user_inserted=True)

        # redirect_to_path unchanged; no team membership created
        self.assertEqual(inv_doc.redirect_to_path, "/forms")
        self.assertEqual(self._get_team_memberships(invitee_email), [])
        frappe.delete_doc("User Invitation", inv_doc.name, force=True)

    # --- default team creation guard (bug fix) ---

    def test_no_default_team_created_for_invited_user(self):
        """
        When a user receives the Forms Pro role but has a pending invitation,
        the role-change hook must NOT create a default team — the invitation
        redirect will place them in the correct inviting team instead.
        """
        invitee_email = self._create_user(with_forms_pro_role=False)
        owner = self._create_user()
        team_id = self._create_team(owner)

        # Simulate a pending invitation (exists before the user accepts)
        frappe.get_doc(
            {
                "doctype": "User Invitation",
                "email": invitee_email,
                "app_name": "forms_pro",
                "redirect_to_path": f"/api/v2/method/forms_pro.api.team.add_member_to_team_via_invitation?team_id={team_id}",
                "roles": [{"role": FORMS_PRO_ROLE}],
                "invited_by": owner,
                "status": "Pending",
            }
        ).insert(ignore_permissions=True)
        frappe.db.commit()

        memberships_before = self._get_team_memberships(invitee_email)

        # Assigning the Forms Pro role is what Frappe does on invitation acceptance;
        # the hook must skip default team creation here.
        user = frappe.get_doc("User", invitee_email)
        user.append_roles(FORMS_PRO_ROLE)
        user.save(ignore_permissions=True)
        frappe.db.commit()

        memberships_after = self._get_team_memberships(invitee_email)
        self.assertEqual(
            len(memberships_before),
            len(memberships_after),
            "A default team must not be created for an invited user",
        )
