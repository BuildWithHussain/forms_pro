import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.api.team import get_team_for_manage
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
