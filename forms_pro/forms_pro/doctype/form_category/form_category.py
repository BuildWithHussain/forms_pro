# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FormCategory(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        color: DF.Data | None
        description: DF.TextEditor | None
        order: DF.Int | None
        title: DF.Data
    # end: auto-generated types

    def validate(self):
        """Validate category settings"""
        # Validate color format if provided
        if self.color and not self.color.startswith("#"):
            # Add # if missing
            self.color = "#" + self.color.lstrip("#")
        
        # Validate hex color format
        if self.color:
            import re
            if not re.match(r"^#[0-9A-Fa-f]{6}$", self.color):
                frappe.throw("Color must be a valid hex color code (e.g., #3b82f6)", frappe.ValidationError)
        
        # Ensure order is not negative
        if self.order is not None and self.order < 0:
            frappe.throw("Order cannot be negative", frappe.ValidationError)

