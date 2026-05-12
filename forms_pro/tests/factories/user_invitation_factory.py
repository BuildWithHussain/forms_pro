from typing import Any

from faker import Faker
from frappe.core.doctype.user_invitation.user_invitation import UserInvitation
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.roles import FORMS_PRO_ROLE

_fake = Faker()


class UserInvitationFactory(BaseFactory[UserInvitation]):
    doctype = "User Invitation"

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "email": self.overrides.get("email", _fake.unique.email()),
            "redirect_to_path": self.overrides.get("redirect_to_path", "/forms"),
            "invited_by": self.overrides.get("invited_by") or "Administrator",
            "status": self.overrides.get("status") or "Pending",
        }

    @property
    def to_forms_pro_app(self) -> dict[str, Any]:
        return {
            "app_name": "forms_pro",
            "redirect_to_path": "/forms",
            "roles": [{"role": FORMS_PRO_ROLE}],
        }
