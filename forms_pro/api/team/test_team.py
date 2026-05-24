import frappe
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase

from forms_pro.api.team import (
    get_team_for_manage,
    get_team_members,
    invite_team_members,
    remove_member_from_team,
    save,
    toggle_can_edit_team,
)
from forms_pro.tests.factories.fp_team_factory import FPTeamFactory
from forms_pro.tests.factories.user_factory import UserFactory


class TestGetTeamForManage(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        # Fresh user with no Forms Pro role → no doctype-level perm on FP Team.
        self.outsider = UserFactory.create()

    def test_returns_team_when_user_has_read(self) -> None:
        result = get_team_for_manage(team_id=self.team.name)
        self.assertEqual(result["name"], self.team.name)
        self.assertEqual(result["team_name"], self.team.team_name)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_team_for_manage(team_id=self.team.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_team_for_manage(team_id="MISSING_TEAM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestGetTeamMembers(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        self.outsider = UserFactory.create()

    def test_admin_can_list_members(self) -> None:
        result = get_team_members(team_id=self.team.name)
        self.assertIsInstance(result, list)

    def test_raises_403_when_user_lacks_read(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                get_team_members(team_id=self.team.name)
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            get_team_members(team_id="MISSING_TEAM_XYZ")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestInviteTeamMembers(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        self.outsider = UserFactory.create()

    def test_raises_403_when_user_lacks_write(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                invite_team_members(team_id=self.team.name, emails=["x@y.z"])
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            invite_team_members(team_id="MISSING_TEAM_XYZ", emails=["x@y.z"])
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestToggleCanEditTeam(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        self.outsider = UserFactory.create()

    def test_raises_403_when_user_lacks_write(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                toggle_can_edit_team(team_id=self.team.name, member_email="x@y.z")
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            toggle_can_edit_team(team_id="MISSING_TEAM_XYZ", member_email="x@y.z")
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestSaveTeam(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        self.outsider = UserFactory.create()

    def test_admin_can_save_team(self) -> None:
        save(team_id=self.team.name, fields={"team_name": "Renamed"})
        self.assertEqual(frappe.db.get_value("FP Team", self.team.name, "team_name"), "Renamed")

    def test_raises_403_when_user_lacks_write(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                save(team_id=self.team.name, fields={"team_name": "Hijacked"})
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            save(team_id="MISSING_TEAM_XYZ", fields={"team_name": "X"})
        self.assertEqual(ctx.exception.http_status_code, 404)


class TestRemoveMemberFromTeam(IntegrationTestCase):
    def setUp(self) -> None:
        self.team = FPTeamFactory.create()
        self.outsider = UserFactory.create()

    def test_raises_403_when_user_lacks_write(self) -> None:
        with self.set_user(self.outsider.name):
            with self.assertRaises(frappe.PermissionError) as ctx:
                remove_member_from_team(team_id=self.team.name, member_email="x@y.z")
            self.assertEqual(ctx.exception.http_status_code, 403)

    def test_raises_404_when_team_missing(self) -> None:
        with self.assertRaises(frappe.DoesNotExistError) as ctx:
            remove_member_from_team(team_id="MISSING_TEAM_XYZ", member_email="x@y.z")
        self.assertEqual(ctx.exception.http_status_code, 404)
