# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


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
        ]
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

        return {
            "fieldname": self.fieldname,
            "fieldtype": _fieldtype,
            "label": self.label,
            "reqd": self.reqd,
            "options": self.options,
            "description": self.description,
            "default": self.default,
        }
