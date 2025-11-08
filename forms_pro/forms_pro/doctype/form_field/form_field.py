# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FormField(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        default: DF.SmallText | None
        description: DF.SmallText | None
        fieldname: DF.Data
        fieldtype: DF.Literal[
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
            "Signature",
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

        # Map form field types back to Frappe field types
        if self.fieldtype == "Email":
            _fieldtype = "Data"
            self.options = "Email"
        elif self.fieldtype == "Number":
            _fieldtype = "Int"
        elif self.fieldtype == "Int":
            _fieldtype = "Int"
        elif self.fieldtype == "Float":
            _fieldtype = "Float"
        elif self.fieldtype == "Currency":
            _fieldtype = "Currency"
        elif self.fieldtype == "Date Time":
            _fieldtype = "Datetime"
        elif self.fieldtype == "Date Range":
            _fieldtype = "Data"
        elif self.fieldtype == "Time Picker":
            _fieldtype = "Time"
        elif self.fieldtype == "Switch":
            _fieldtype = "Check"
        elif self.fieldtype == "Checkbox":
            _fieldtype = "Check"
        elif self.fieldtype == "Textarea":
            _fieldtype = "Text"
        elif self.fieldtype == "Text Editor":
            _fieldtype = "Text Editor"
        elif self.fieldtype == "Phone":
            _fieldtype = "Data"  # Phone maps to Data in Frappe
        elif self.fieldtype == "File Uploader":
            # Special handling: if fieldname is "image", use "Attach Image"
            # Otherwise, use "Attach"
            if self.fieldname.lower() == "image":
                _fieldtype = "Attach Image"
            else:
                _fieldtype = "Attach"
        elif self.fieldtype == "Table":
            _fieldtype = "Table"
        elif self.fieldtype == "Rating":
            _fieldtype = "Rating"
        elif self.fieldtype == "Signature":
            # Signature fields are stored as Attach Image in Frappe
            _fieldtype = "Attach Image"
        elif self.fieldtype == "Select":
            # Check if options is a valid DocType name - if so, convert to Link
            # This handles the case where Link fields are stored as Select in forms
            if self.options:
                options_str = self.options.strip()
                # Check if it looks like a DocType name (single word, no newlines, no commas)
                if ("\n" not in options_str and 
                    "," not in options_str and 
                    len(options_str.split()) <= 3):  # DocType names are usually 1-3 words
                    # Check if it's a valid DocType
                    try:
                        # Use frappe.db.exists to check if DocType exists
                        if frappe.db.exists("DocType", options_str):
                            _fieldtype = "Link"
                    except Exception:
                        pass  # If check fails, keep as Select
        # All other types (Data, Password, Date) map directly

        # Special validation: Frappe requires fields named "image" to be "Attach Image"
        if self.fieldname.lower() == "image" and _fieldtype != "Attach Image":
            _fieldtype = "Attach Image"

        return {
            "fieldname": self.fieldname,
            "fieldtype": _fieldtype,
            "label": self.label,
            "reqd": self.reqd,
            "options": self.options,
            "description": self.description,
            "default": self.default,
        }
