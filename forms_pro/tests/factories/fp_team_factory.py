from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.forms_pro.doctype.fp_team.fp_team import FPTeam

_fake = Faker()


class FPTeamFactory(BaseFactory[FPTeam]):
    doctype = "FP Team"

    @property
    def default_attributes(self) -> dict[str, Any]:
        return {"team_name": f"{_fake.word().capitalize()} Team"}
