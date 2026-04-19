# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

# Maps Forms Pro field types to Frappe CustomField fieldtypes.
# When adding a new field type:
#   1. Add the option to form_field.json  →  DF.Literal regenerates automatically
#   2. Add an entry here
#   3. Add an entry to FIELD_TYPE_DEFINITIONS in frontend/src/config/fieldTypes.ts
FORM_TO_FRAPPE_FIELDTYPE: dict[str, dict] = {
    "Attach": {"fieldtype": "Attach"},
    "Data": {"fieldtype": "Data"},
    "Number": {"fieldtype": "Int"},
    "Email": {"fieldtype": "Data", "options": "Email"},
    "Date": {"fieldtype": "Date"},
    "Date Time": {"fieldtype": "Datetime"},
    "Date Range": {"fieldtype": "Data"},
    "Time Picker": {"fieldtype": "Time"},
    "Password": {"fieldtype": "Password"},
    "Select": {"fieldtype": "Select"},
    "Phone": {"fieldtype": "Phone"},
    "Switch": {"fieldtype": "Check"},
    "Textarea": {"fieldtype": "Text"},
    "Text Editor": {"fieldtype": "Text Editor"},
    "Link": {"fieldtype": "Link"},
    "Checkbox": {"fieldtype": "Check"},
    "Rating": {"fieldtype": "Rating"},
    "Table": {"fieldtype": "Table"},
    "Multiselect": {"fieldtype": "JSON"},
}


class FormField(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        conditional_logic: DF.Code | None
        default: DF.SmallText | None
        description: DF.SmallText | None
        fieldname: DF.Data
        fieldtype: DF.Literal[
            "Attach",
            "Data",
            "Number",
            "Email",
            "Date",
            "Date Time",
            "Date Range",
            "Time Picker",
            "Password",
            "Select",
            "Switch",
            "Textarea",
            "Text Editor",
            "Link",
            "Checkbox",
            "Rating",
            "Phone",
            "Table",
            "Multiselect",
        ]
        hidden: DF.Check
        label: DF.Data
        options: DF.SmallText | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        reqd: DF.Check
    # end: auto-generated types

    @property
    def to_frappe_field(self) -> dict:
        mapping = FORM_TO_FRAPPE_FIELDTYPE.get(self.fieldtype, {})
        return {
            "fieldname": self.fieldname,
            "fieldtype": mapping.get("fieldtype", self.fieldtype),
            "label": self.label,
            "reqd": self.reqd,
            "options": mapping.get("options", self.options),
            "description": self.description,
            "default": self.default,
        }
