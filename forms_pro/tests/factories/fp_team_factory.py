from typing import Any

import frappe
from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

_fake = Faker()


class FPTeamFactory(BaseFactory):
    doctype = "FP Team"

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {"team_name": f"{_fake.word().capitalize()} Team"}

    @staticmethod
    def __del_override__(_self: Any) -> None:
        try:
            if frappe.db.exists("FP Team", _self.name):
                frappe.delete_doc("FP Team", _self.name, force=True, ignore_permissions=True)
        except Exception:
            pass
