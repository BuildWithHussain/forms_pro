from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.forms_pro.doctype.form.form import Form

_fake = Faker()


class FormFactory(BaseFactory[Form]):
    """
    Builds a Form linked to a placeholder custom DocType (created via
    `LinkedFormDoctypeFactory`) and a fresh `FP Team`. Pass
    `linked_doctype=<name>` to attach to an existing DocType (e.g. for
    multi-form scoping tests) and `linked_team_id=<name>` to bind to an
    existing team.
    """

    doctype = "Form"

    @property
    def default_attributes(self) -> dict[str, Any]:
        from forms_pro.tests.factories.fp_team_factory import FPTeamFactory
        from forms_pro.tests.factories.linked_form_doctype_factory import (
            LinkedFormDoctypeFactory,
        )

        return {
            "title": _fake.unique.sentence(nb_words=3).rstrip("."),
            "linked_doctype": (
                self.overrides.get("linked_doctype") or LinkedFormDoctypeFactory.create().name
            ),
            "linked_team_id": (self.overrides.get("linked_team_id") or FPTeamFactory.create().name),
        }
