import frappe


@frappe.whitelist(allow_guest=True)
def get_form_by_route(route: str) -> dict:
    form_id = frappe.db.get_value("Form", {"route": route}, pluck="name")
    return get_form(form_id)


@frappe.whitelist(allow_guest=True)
def get_form(form_id: str) -> dict:
    form = frappe.get_doc(
        "Form",
        form_id,
    )
    return {
        "name": form.name,
        "title": form.title,
        "description": form.description,
        "fields": form.fields,
        "route": form.route,
        "is_published": form.is_published,
        "allow_incomplete": form.allow_incomplete,
    }


@frappe.whitelist()
def get_doctype_fields(doctype: str) -> dict:
    doctype = frappe.get_doc("DocType", doctype)
    fields = doctype.fields

    FIELDTYPES_TO_REMOVE = [
        "Section Break",
        "HTML",
        "Button",
        "Column Break",
        "Tab Break",
        "Barcode",
        "Dynamic Link",
        "Fold",
    ]

    fields = [field for field in fields if field.fieldtype not in FIELDTYPES_TO_REMOVE]

    return fields


@frappe.whitelist()
def get_doctype_list() -> list[str]:
    return frappe.db.get_list(
        "DocType",
        filters={"istable": 0},
        pluck="name",
        order_by="name",
        limit_page_length=99999,
    )


@frappe.whitelist()
def auto_populate_fields_from_doctype(form_id: str, replace_existing: bool = False) -> dict:
    """
    Auto-populate form fields from the linked DocType.
    
    Args:
        form_id: The Form document name
        replace_existing: If True, replace all existing fields. If False, append new fields (skipping duplicates)
    
    Returns:
        dict with 'success', 'fields_added', and 'message' keys
    """
    form = frappe.get_doc("Form", form_id)
    
    # Check if form is published
    if form.is_published:
        frappe.throw("Cannot modify fields of a published form. Please unpublish first.")
    
    # Check if linked_doctype exists
    if not form.linked_doctype:
        frappe.throw("Form must have a linked DocType to auto-populate fields.")
    
    # Get doctype fields
    doctype_fields = get_doctype_fields(form.linked_doctype)
    
    if not doctype_fields:
        return {
            "success": False,
            "fields_added": 0,
            "message": "No valid fields found in the linked DocType."
        }
    
    # Field type mapping (matching frontend mapDoctypeFieldForForm)
    # Comprehensive mapping of all Frappe field types to form field types
    FIELD_TYPE_MAP = {
        # Text fields
        "Data": "Data",
        "Small Text": "Textarea",
        "Text": "Textarea",
        "Long Text": "Textarea",
        "Text Editor": "Text Editor",
        "HTML Editor": "Text Editor",
        "Markdown Editor": "Text Editor",
        "Code": "Textarea",
        "JSON": "Textarea",
        
        # Number fields
        "Int": "Number",
        "Float": "Number",
        "Currency": "Number",
        "Percent": "Number",
        
        # Date/Time fields
        "Date": "Date",
        "Datetime": "Date Time",
        "Time": "Time Picker",
        "Duration": "Data",  # Duration not directly supported, map to Data
        
        # Selection fields
        "Select": "Select",
        "Autocomplete": "Data",  # Autocomplete maps to Data with autocomplete behavior
        
        # Boolean fields
        "Check": "Checkbox",
        
        # Link fields (map to Select or Data based on options)
        "Link": "Select",  # Link fields become Select dropdowns
        "Dynamic Link": "Data",  # Dynamic Link not directly supported
        
        # File/Attachment fields
        "Attach": "File Uploader",
        "Attach Image": "File Uploader",
        "Image": "File Uploader",
        "Signature": "File Uploader",
        
        # Special fields
        "Password": "Password",
        "Rating": "Rating",
        "Color": "Data",  # Color picker not directly supported
        "Geolocation": "Data",  # Geolocation not directly supported
        "Phone": "Data",  # Phone with validation
        "Email": "Email",  # Email field type
        
        # Read-only/Display fields
        "Read Only": "Data",  # Read-only fields as Data (disabled)
        "Heading": "Data",  # Heading as Data
        "HTML": "Textarea",  # HTML content as Textarea
        "Icon": "Data",  # Icon field as Data
        
        # Layout fields (these are filtered out but included for completeness)
        "Section Break": None,  # Filtered out
        "Column Break": None,  # Filtered out
        "Tab Break": None,  # Filtered out
        "Fold": None,  # Filtered out
        "Button": None,  # Filtered out
        "Barcode": None,  # Filtered out
    }
    
    # Get existing fieldnames if not replacing
    existing_fieldnames = set()
    if not replace_existing:
        existing_fieldnames = {field.fieldname for field in form.fields if field.fieldname}
    
    # Map and create form fields
    new_fields = []
    fields_added = 0
    start_idx = 1 if replace_existing else len(form.fields) + 1
    current_idx = start_idx
    
    # Helper function to check if a string is a valid DocType name
    def is_doctype_name(options_str):
        """Check if options string looks like a DocType name"""
        if not options_str:
            return False
        options_str = options_str.strip()
        # DocType names are typically single words, Title Case, no newlines
        # and exist in the system
        if "\n" in options_str or len(options_str.split()) > 1:
            return False
        # Check if it's a valid DocType
        try:
            return frappe.db.exists("DocType", options_str)
        except:
            return False
    
    for doctype_field in doctype_fields:
        # Skip if fieldname already exists (when not replacing)
        if doctype_field.fieldname in existing_fieldnames:
            continue
        
        # Map field type
        mapped_fieldtype = FIELD_TYPE_MAP.get(doctype_field.fieldtype)
        
        # Skip if field type is None (layout fields) or not mapped
        if not mapped_fieldtype:
            continue
        
        # Valid form field types that are supported
        valid_form_fieldtypes = [
            "Data", "Number", "Email", "Date", "Date Time", "Date Range",
            "Time Picker", "Password", "Select", "Switch", "Textarea",
            "Text Editor", "Checkbox", "File Uploader", "Rating"
        ]
        
        if mapped_fieldtype not in valid_form_fieldtypes:
            # Fallback to Data for unmapped types
            mapped_fieldtype = "Data"
        
        # Special handling for Data fields with DocType options (Link fields disguised as Data)
        # If a Data field has options that is a valid DocType name, convert it to Select
        # This handles cases where Link fields are stored as Data fields with DocType in options
        if doctype_field.fieldtype == "Data" and doctype_field.options:
            if is_doctype_name(doctype_field.options):
                # This is likely a Link field stored as Data - convert to Select
                mapped_fieldtype = "Select"
                # Keep the DocType name in options for the frontend to handle
            elif "email" in doctype_field.fieldname.lower() or "email" in (doctype_field.label or "").lower():
                # Email field detection
                mapped_fieldtype = "Email"
        
        # Special handling for Link fields - they're already mapped to Select above
        # Preserve the DocType name in options
        
        # Special handling for Email field type detection (if not already handled above)
        if doctype_field.fieldtype == "Data" and mapped_fieldtype == "Data" and (
            "email" in doctype_field.fieldname.lower() or
            "email" in (doctype_field.label or "").lower()
        ):
            mapped_fieldtype = "Email"
        
        # Create form field
        form_field = {
            "idx": current_idx,
            "label": doctype_field.label or doctype_field.fieldname,
            "fieldname": doctype_field.fieldname,
            "fieldtype": mapped_fieldtype,
            "reqd": 1 if doctype_field.reqd else 0,
            "options": doctype_field.options or "",
            "default": doctype_field.default or "",
            "description": doctype_field.description or "",
        }
        
        new_fields.append(form_field)
        fields_added += 1
        current_idx += 1  # Increment idx for next field
    
    if fields_added == 0:
        return {
            "success": False,
            "fields_added": 0,
            "message": "No new fields to add. All fields may already exist or be unsupported."
        }
    
    # Update form fields
    if replace_existing:
        form.fields = []
    
    # Add new fields
    for field_data in new_fields:
        form.append("fields", field_data)
    
    # Re-index all fields to ensure sequential ordering
    # This is important to maintain proper field order
    for idx, field in enumerate(form.fields, start=1):
        field.idx = idx
    
    form.save(ignore_permissions=True)
    
    return {
        "success": True,
        "fields_added": fields_added,
        "message": f"Successfully added {fields_added} field(s) from DocType."
    }
