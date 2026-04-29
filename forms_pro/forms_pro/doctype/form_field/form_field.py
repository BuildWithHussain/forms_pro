# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import escape_html

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
    "Heading 1": {"fieldtype": "HTML"},
    "Heading 2": {"fieldtype": "HTML"},
    "Heading 3": {"fieldtype": "HTML"},
}


_DISPLAY_ONLY_FIELDTYPES = {"Heading 1", "Heading 2", "Heading 3"}


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
            "Heading 1",
            "Heading 2",
            "Heading 3",
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
        _fieldtype = self.fieldtype

        if self.fieldtype == "Email":
            _fieldtype = "Data"
            self.options = "Email"
        elif self.fieldtype == "Number":
            _fieldtype = "Int"
        elif self.fieldtype == "Date Time":
            _fieldtype = "Datetime"
        elif self.fieldtype == "Date Range":
            _fieldtype = "Data"
        elif self.fieldtype == "Time Picker":
            _fieldtype = "Time"
        elif self.fieldtype == "Switch" or self.fieldtype == "Checkbox":
            _fieldtype = "Check"
        elif self.fieldtype == "Textarea":
            _fieldtype = "Text"
        elif self.fieldtype == "Multiselect":
            _fieldtype = "JSON"
        elif self.fieldtype in _DISPLAY_ONLY_FIELDTYPES:
            _fieldtype = "HTML"

        return {
            "fieldname": self.fieldname,
            "fieldtype": _fieldtype,
            "label": self.label,
            "reqd": self.reqd,
            "options": self.get_options(),
            "description": self.description,
            "default": self.default,
        }

    def get_options(self) -> str | None:
        if self.fieldtype in _DISPLAY_ONLY_FIELDTYPES:
            HEADING_MAP = {
                "Heading 1": "h1",
                "Heading 2": "h2",
                "Heading 3": "h3",
            }
            tag = HEADING_MAP.get(self.fieldtype, "h2")
            return f"<{tag}>{escape_html(self.label or '')}</{tag}>"

        return self.options
