from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.roles import FORMS_PRO_ROLE

_fake = Faker()


class UserFactory(BaseFactory):
    doctype = "User"

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {
            "email": _fake.unique.email(),
            "first_name": _fake.first_name(),
            "last_name": _fake.last_name(),
        }

    @property
    def with_forms_pro_role(self) -> dict[str, Any]:
        # Frappe accepts child table rows as dicts in the initial doc dict.
        # on_update fires with the role already set, so the default team is created.
        return {"roles": [{"role": FORMS_PRO_ROLE}]}
