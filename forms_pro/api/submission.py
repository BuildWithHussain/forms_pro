import frappe
from frappe.core.api.file import get_max_file_size
from forms_pro.api.form import can_guest_upload_files


@frappe.whitelist(allow_guest=True)
def submit_form_response(form_id: str, form_data: list[dict]):
    """Submit form response, handling guest permissions and file uploads"""
    form = frappe.get_doc("Form", form_id)
    linked_doctype = form.linked_doctype
    user = frappe.session.user
    
    # Check if guest submission is allowed
    if user == "Guest":
        if form.login_required:
            frappe.throw("You must login to submit this form", frappe.PermissionError)
        if not (hasattr(form, 'allow_anonymous') and form.allow_anonymous):
            frappe.throw("Anonymous submissions are not allowed for this form", frappe.PermissionError)
    
    # Get form fields to identify file upload fields
    meta = frappe.get_meta(linked_doctype)
    files = []
    
    submission = frappe.new_doc(linked_doctype)
    
    # Set ignore_mandatory flag if allow_incomplete is enabled
    if form.allow_incomplete:
        submission.flags.ignore_mandatory = True
    
    # Process form data
    for data in form_data:
        fieldname = data.get("fieldname")
        value = data.get("value", "")
        
        if not fieldname:
            continue
        
        df = meta.get_field(fieldname)
        
        # Handle file uploads
        if df and df.fieldtype in ("Attach", "Attach Image"):
            # Check if this is a base64 encoded file
            if value and isinstance(value, str) and "data:" in value and "base64" in value:
                # Check guest upload permissions
                if user == "Guest" and not can_guest_upload_files():
                    frappe.throw(
                        "Guest file uploads are not allowed. Please contact the administrator.",
                        frappe.PermissionError
                    )
                
                # Validate file size
                max_size = form.max_attachment_size if hasattr(form, 'max_attachment_size') and form.max_attachment_size else None
                if not max_size:
                    max_size = get_max_file_size() / 1024 / 1024  # Convert to MB
                
                # Extract file data
                try:
                    header, encoded = value.split(",", 1)
                    # Get file size from base64 (approximate)
                    file_size_mb = (len(encoded) * 3 / 4) / 1024 / 1024
                    
                    if file_size_mb > max_size:
                        frappe.throw(
                            f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size} MB)",
                            frappe.ValidationError
                        )
                    
                    files.append((fieldname, value))
                    # Set empty initially, will be updated after file is saved
                    submission.set(fieldname, "")
                    continue
                except ValueError:
                    frappe.throw("Invalid file data format", frappe.ValidationError)
            elif not value:
                # Empty value for file field - file is being removed or not set
                # Note: For new documents, there's nothing to delete
                pass
        
        # Set regular field value
        submission.set(fieldname, value)
    
    # Insert the document
    if form.allow_incomplete or files:
        submission.insert(ignore_permissions=True, ignore_mandatory=True)
    else:
        submission.insert(ignore_permissions=True)
    
    # Handle file uploads
    if files:
        for f in files:
            fieldname, filedata = f
            
            # Remove earlier attached file if exists
            if submission.get(fieldname):
                remove_file_by_url(submission.get(fieldname), doctype=linked_doctype, name=submission.name)
            
            # Parse file data
            try:
                header, dataurl = filedata.split(",", 1)
                # Extract filename from header (e.g., "data:image/png;base64")
                filename = header.split(";")[0].split(":")[1] if ":" in header else "file"
                if "/" in filename:
                    filename = filename.split("/")[-1] or "file"
                
                # Create File document
                _file = frappe.get_doc({
                    "doctype": "File",
                    "file_name": filename,
                    "attached_to_doctype": linked_doctype,
                    "attached_to_name": submission.name,
                    "content": dataurl,
                    "decode": True,
                })
                _file.save(ignore_permissions=True)
                
                # Update submission with file URL
                submission.set(fieldname, _file.file_url)
            except Exception as e:
                frappe.throw(f"Error uploading file: {str(e)}", frappe.ValidationError)
        
        # Save submission with file URLs
        submission.save(ignore_permissions=True)
    
    return submission.name
