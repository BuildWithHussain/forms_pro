"""
Audit coverage for forms_pro.api.user.

These endpoints gate on session state, not DocShare, so they take no
`@require_permission` decorator. The tests below document current
behavior so future regressions are caught.
"""

from frappe.tests.utils import FrappeTestCase as IntegrationTestCase

from forms_pro.api.user import get_current_user, get_user, get_user_teams
from forms_pro.tests import FORMS_PRO_TEST_USER


class TestGetUser(IntegrationTestCase):
    def test_returns_basic_payload_for_existing_user(self) -> None:
        result = get_user(user=FORMS_PRO_TEST_USER)
        self.assertIsNotNone(result)
        self.assertIn("full_name", result)
        self.assertIn("user_image", result)

    def test_returns_none_for_missing_user(self) -> None:
        self.assertIsNone(get_user(user="missing_user_xyz@example.com"))


class TestGetCurrentUser(IntegrationTestCase):
    def test_returns_session_user_payload(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            result = get_current_user()
        self.assertEqual(result["email"], FORMS_PRO_TEST_USER)
        self.assertIn("roles", result)
        self.assertIn("has_desk_access", result)


class TestGetUserTeams(IntegrationTestCase):
    def test_returns_list_for_real_user(self) -> None:
        with self.set_user(FORMS_PRO_TEST_USER):
            result = get_user_teams()
        self.assertIsInstance(result, list)

    def test_returns_empty_for_guest(self) -> None:
        with self.set_user("Guest"):
            self.assertEqual(get_user_teams(), [])
