from typing import Any

from faker import Faker
from frappe.model.document import Document
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.utils.form_generator import LINKED_FORM_FIELDOPTIONS, SUBMISSION_STATUS_FIELDOPTIONS

_fake = Faker()


class LinkedFormDoctypeFactory(BaseFactory[Document]):
    """
    Builds a placeholder custom DocType that mirrors what
    `forms_pro.utils.form_generator.FormGenerator` would create for a new
    Form. The DocType carries `fp_submission_status` and `fp_linked_form`
    so a Form pointing at it accepts submissions immediately.

    Use as the linked_doctype for `FormFactory`.
    """

    doctype = "DocType"

    @property
    def default_attributes(self) -> dict[str, Any]:
        name = f"formspro_test_{_fake.unique.lexify('??????').lower()}"
        return {
            "name": name,
            "module": "User Forms",
            "custom": 1,
            "track_changes": 1,
            "issingle": 0,
            "istable": 0,
            "is_submittable": 0,
            "is_virtual": 0,
            "editable_grid": 0,
            "fields": [
                {"fieldtype": "Section Break"},
                SUBMISSION_STATUS_FIELDOPTIONS,
                LINKED_FORM_FIELDOPTIONS,
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "create": 1,
                    "delete": 1,
                    "email": 1,
                    "export": 1,
                    "print": 1,
                    "read": 1,
                    "report": 1,
                    "share": 1,
                    "write": 1,
                    "submit": 0,
                }
            ],
        }
