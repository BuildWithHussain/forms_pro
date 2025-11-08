# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Form(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from forms_pro.forms_pro.doctype.form_field.form_field import FormField

        allow_incomplete: DF.Check
        description: DF.TextEditor | None
        fields: DF.Table[FormField]
        is_published: DF.Check
        linked_doctype: DF.Link
        login_required: DF.Check
        metadata: DF.Code | None
        route: DF.Data | None
        title: DF.Data
    # end: auto-generated types

    def validate(self):
        """Validate form settings"""
        # Ensure allow_anonymous and login_required are mutually exclusive
        if hasattr(self, 'allow_anonymous') and self.allow_anonymous and self.login_required:
            frappe.throw("Cannot enable both 'Allow Anonymous Submissions' and 'Login Required'", frappe.ValidationError)
        
        # Validate max_attachment_size if set (0 or None means use system default)
        if hasattr(self, 'max_attachment_size') and self.max_attachment_size is not None and self.max_attachment_size != 0:
            if self.max_attachment_size < 0:
                frappe.throw("Max Attachment Size cannot be negative", frappe.ValidationError)
    
    @property
    def linked_doctype_doc(self) -> Document:
        return frappe.get_doc("DocType", self.linked_doctype)

    def generate_initial_route(self) -> str:
        return "s/forms_pro_" + frappe.utils.random_string(8)

    def before_insert(self) -> None:
        self.status = "Draft"
        self.is_published = False
        self.route = self.generate_initial_route()

    def on_update(self) -> None:
        # Prevent changing allow_anonymous if form is published (similar to linked_doctype)
        if self.is_published and self.has_value_changed("allow_anonymous"):
            frappe.throw("Cannot change 'Allow Anonymous Submissions' for published forms. Please unpublish first.", frappe.ValidationError)
        
        self.set_doctype_fields()

    def set_doctype_fields(self) -> None:
        doctype_doc = self.linked_doctype_doc
        existing_fields = {f.fieldname: f for f in doctype_doc.fields}

        # Track fieldname changes and new fields
        fieldname_changes = {}  # old_fieldname -> new_fieldname
        new_fields = []

        for field in self.fields:
            _field = field.to_frappe_field
            # Check if this fieldname exists in the doctype
            if _field["fieldname"] in existing_fields:
                # Field exists, check if any properties have changed
                existing_field = existing_fields[_field["fieldname"]]
                # Update the existing field with new properties
                for prop in ["label", "fieldtype", "reqd", "options", "description", "default"]:
                    if prop in _field and hasattr(existing_field, prop):
                        setattr(existing_field, prop, _field[prop])
            else:
                # This is a new field, check if it's a renamed field
                # Look for a field with same label but different fieldname
                found_renamed = False
                for existing_fieldname, existing_field in existing_fields.items():
                    if (
                        hasattr(existing_field, "label")
                        and existing_field.label == _field["label"]
                        and existing_fieldname != _field["fieldname"]
                    ):
                        # This is a fieldname change
                        fieldname_changes[existing_fieldname] = _field["fieldname"]
                        # Update the existing field's fieldname and other properties
                        existing_field.fieldname = _field["fieldname"]
                        for prop in ["fieldtype", "reqd", "options", "description", "default"]:
                            if prop in _field and hasattr(existing_field, prop):
                                setattr(existing_field, prop, _field[prop])
                        found_renamed = True
                        break

                if not found_renamed:
                    # This is truly a new field
                    new_fields.append(_field)

        # Add new fields to the doctype
        for field in new_fields:
            doctype_doc.append(
                "fields",
                {
                    "label": field["label"],
                    "fieldname": field["fieldname"],
                    "fieldtype": field["fieldtype"],
                    "reqd": field["reqd"],
                    "options": field["options"],
                    "description": field["description"],
                    "default": field["default"],
                },
            )

        # Save the doctype with all changes
        doctype_doc.save(ignore_permissions=True)
