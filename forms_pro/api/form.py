import frappe
import os
import re
import json


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
        "linked_doctype": form.linked_doctype,  # Include linked_doctype for filter support
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


def get_field_query_filters(parent_doctype: str, fieldname: str) -> dict:
    """
    Parse the parent DocType's JavaScript file to extract set_query filters for a specific field.
    
    Args:
        parent_doctype: The parent DocType name
        fieldname: The field name to get filters for
    
    Returns:
        dict with filters to apply, or empty dict if no filters found
    """
    if not parent_doctype or not fieldname:
        frappe.log_error(f"get_field_query_filters: Missing parameters - parent_doctype={parent_doctype}, fieldname={fieldname}")
        return {}
    
    try:
        # Get the DocType document to find its module
        doctype_doc = frappe.get_doc("DocType", parent_doctype)
        module = doctype_doc.module
        
        # Construct the path to the JavaScript file
        # Format: apps/{app_name}/{app_name}/{module}/doctype/{doctype_name}/{doctype_name}.js
        app_name = frappe.db.get_value("Module Def", module, "app_name")
        if not app_name:
            return {}
        
        # Try to find the JS file path
        # First, try the standard path structure
        possible_paths = [
            os.path.join(
                frappe.get_app_path(app_name),
                frappe.scrub(app_name),
                frappe.scrub(module),
                "doctype",
                frappe.scrub(parent_doctype),
                f"{frappe.scrub(parent_doctype)}.js"
            ),
            # Alternative path structure (some apps use different conventions)
            os.path.join(
                frappe.get_app_path(app_name),
                frappe.scrub(app_name),
                frappe.scrub(module),
                "doctype",
                frappe.scrub(parent_doctype),
                f"{frappe.scrub(parent_doctype)}.js"
            ),
        ]
        
        js_content = None
        js_path = None
        
        for path in possible_paths:
            if os.path.exists(path):
                js_path = path
                break
        
        # If not found, try to search in the app directory
        if not js_path:
            app_path = frappe.get_app_path(app_name)
            # Search for the JS file
            for root, dirs, files in os.walk(app_path):
                if f"{frappe.scrub(parent_doctype)}.js" in files:
                    js_path = os.path.join(root, f"{frappe.scrub(parent_doctype)}.js")
                    break
        
        if not js_path or not os.path.exists(js_path):
            frappe.log_error(f"get_field_query_filters: JS file not found for {parent_doctype} at {js_path}")
            return {}
        
        # Read the JavaScript file
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        if not js_content:
            frappe.log_error(f"get_field_query_filters: JS file is empty for {parent_doctype}")
            return {}
        
        # Pattern to match: frm.set_query('fieldname', function() { return { filters: {...} }; })
        # This regex handles various formats:
        # - frm.set_query('fieldname', function() { return { filters: {...} }; })
        # - frm.set_query("fieldname", function() { return { filters: {...} }; })
        # - frm.set_query('fieldname', function() { return { filters: {...} } })
        
        # Escape the fieldname for regex
        escaped_fieldname = re.escape(fieldname)
        
        # Pattern to find set_query for this specific field
        # Match: frm.set_query('fieldname' or "fieldname", function() { return { filters: {...} }; })
        # Handle tabs, newlines, and various whitespace
        # First try a comprehensive pattern
        pattern = rf"frm\.set_query\(['\"]{escaped_fieldname}['\"]\s*,\s*function\s*\([^)]*\)\s*{{\s*return\s*{{\s*filters:\s*{{\s*([^}}]+)\s*}}\s*}}\s*;?\s*}}\s*\)"
        
        match = re.search(pattern, js_content, re.DOTALL | re.MULTILINE)
        
        if not match:
            # Try a simpler pattern that matches the filters object more flexibly
            # This pattern looks for frm.set_query('fieldname', ...) and then finds filters: {...}
            # Handle tabs and newlines
            pattern2 = rf"frm\.set_query\(['\"]{escaped_fieldname}['\"]\s*,\s*[^}}]*?filters:\s*{{\s*([^}}]+)\s*}}"
            match = re.search(pattern2, js_content, re.DOTALL | re.MULTILINE)
        
        if not match:
            # Try even simpler - just find the fieldname and then filters
            pattern3 = rf"set_query\(['\"]{escaped_fieldname}['\"][\s\S]*?filters:\s*{{\s*([^}}]+)\s*}}"
            match = re.search(pattern3, js_content, re.DOTALL | re.MULTILINE)
        
        if not match:
            frappe.log_error(f"get_field_query_filters: No set_query found for {parent_doctype}.{fieldname}")
            return {}
        
        filters_str = match.group(1).strip()
        frappe.log_error(f"get_field_query_filters: Found filters string for {parent_doctype}.{fieldname}: {filters_str}")
        
        # Parse the filters string into a Python dict
        # The filters string might look like: 'ga_is_partner': 1 or "ga_is_partner": 1
        # We need to convert this to a proper dict
        
        filters = {}
        
        # Pattern to match key-value pairs in the filters object
        # Handles: 'key': value, "key": value, key: value
        # Value can be: number, string (quoted or unquoted), boolean
        filter_pattern = r"['\"]?([a-zA-Z_][a-zA-Z0-9_]*)['\"]?\s*:\s*([^,}\n]+)"
        filter_matches = re.findall(filter_pattern, filters_str)
        
        for key, value in filter_matches:
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present (both single and double)
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            
            # Remove any remaining whitespace
            value = value.strip()
            
            # Try to convert to appropriate type
            if value.isdigit():
                filters[key] = int(value)
            elif value.lower() == 'true':
                filters[key] = True
            elif value.lower() == 'false':
                filters[key] = False
            else:
                # Try to parse as number (float or int)
                try:
                    # Try int first
                    if '.' not in value:
                        filters[key] = int(value)
                    else:
                        filters[key] = float(value)
                except ValueError:
                    # Keep as string (remove quotes if still present)
                    if (value.startswith("'") and value.endswith("'")) or \
                       (value.startswith('"') and value.endswith('"')):
                        filters[key] = value[1:-1]
                    else:
                        filters[key] = value
        
        frappe.log_error(f"get_field_query_filters: Parsed filters for {parent_doctype}.{fieldname}: {filters}")
        return filters
        
    except Exception as e:
        # Log error but don't fail - just return empty filters
        frappe.log_error(
            f"Error parsing field query filters for {parent_doctype}.{fieldname}: {str(e)}",
            "get_field_query_filters"
        )
        return {}


@frappe.whitelist(allow_guest=True)
def get_link_field_options(
    doctype: str, 
    search_term: str = None, 
    limit: int = 20,
    parent_doctype: str = None,
    fieldname: str = None
) -> dict:
    """
    Get options for a Link field (Select field with DocType options).
    Returns a list of records from the specified DocType.
    
    Args:
        doctype: The DocType name to fetch records from
        search_term: Optional search term to filter records
        limit: Maximum number of records to return
        parent_doctype: Optional parent DocType name (to apply field-specific filters)
        fieldname: Optional field name in the parent DocType (to apply field-specific filters)
    
    Returns:
        dict with 'options' list containing {label, value} pairs
    """
    if not doctype:
        return {"options": []}
    
    # Validate that the DocType exists
    if not frappe.db.exists("DocType", doctype):
        return {"options": []}
    
    # Get the DocType meta to find the title field
    meta = frappe.get_meta(doctype)
    title_field = meta.title_field or "name"
    
    # Get field-specific filters from parent DocType if provided
    field_filters = {}
    if parent_doctype and fieldname:
        frappe.log_error(f"get_link_field_options: Attempting to get filters for parent_doctype={parent_doctype}, fieldname={fieldname}")
        field_filters = get_field_query_filters(parent_doctype, fieldname)
        frappe.log_error(f"get_link_field_options: Retrieved field_filters: {field_filters}")
    else:
        frappe.log_error(f"get_link_field_options: No parent_doctype or fieldname provided - parent_doctype={parent_doctype}, fieldname={fieldname}")
    
    # Build filters - merge field filters with search filters
    # Frappe filters format: {key: value} for simple filters, or {and: [...], or: [...]} for complex
    filters = {}
    
    # Start with field-specific filters
    if field_filters:
        # Convert dict filters to list format for Frappe
        # Simple filters: {key: value} becomes [[key, "=", value]]
        filter_list = []
        for key, value in field_filters.items():
            filter_list.append([key, "=", value])
        
        if len(filter_list) == 1:
            # Single filter - use simple format
            filters = {filter_list[0][0]: filter_list[0][2]}
        else:
            # Multiple filters - combine with AND
            filters = {"and": filter_list}
    
    # Add search term filters if provided
    if search_term:
        search_filter = {
            "or": [
                [title_field, "like", f"%{search_term}%"],
                ["name", "like", f"%{search_term}%"],
            ]
        }
        
        # Combine with existing filters
        if filters:
            # We have both field filters and search filters
            # Combine them with AND
            if "and" in filters:
                # Already have AND filters, add search OR to the list
                filters["and"].append(search_filter["or"])
            else:
                # Single field filter in dict format, convert to AND format
                # Convert dict filter to list format
                field_filter_list = []
                for key, value in filters.items():
                    field_filter_list.append([key, "=", value])
                
                # Combine with search filter
                filters = {
                    "and": field_filter_list + [search_filter["or"]]
                }
        else:
            # No field filters, just use search
            filters = search_filter
    
    # Get records
    try:
        # Log the filters being applied for debugging
        frappe.log_error(f"get_link_field_options: Fetching {doctype} with filters: {filters}")
        
        records = frappe.get_list(
            doctype,
            fields=["name", title_field],
            filters=filters,
            limit=limit,
            order_by=title_field or "name",
        )
        
        frappe.log_error(f"get_link_field_options: Found {len(records)} records for {doctype}")
        
        # Format as options for Select component
        options = []
        for record in records:
            label = record.get(title_field) or record.name
            options.append({
                "label": label,
                "value": record.name,
            })
        
        return {"options": options}
    except Exception as e:
        frappe.log_error(f"Error fetching options for {doctype} with filters {filters}: {str(e)}")
        return {"options": []}


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
