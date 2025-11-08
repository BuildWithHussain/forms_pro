import frappe
from frappe import _
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
    
    # Track which form created this submission (for filtering in submissions list)
    # Check if the field exists, if not, we'll add it dynamically
    form_tracking_field = "forms_pro_form_id"
    if meta.has_field(form_tracking_field):
        submission.set(form_tracking_field, form_id)
    else:
        # Field doesn't exist, add it to the DocType dynamically
        try:
            doctype_doc = frappe.get_doc("DocType", linked_doctype)
            # Check if field already exists (race condition check)
            if not any(f.fieldname == form_tracking_field for f in doctype_doc.fields):
                doctype_doc.append("fields", {
                    "fieldname": form_tracking_field,
                    "label": "Forms Pro Form ID",
                    "fieldtype": "Link",
                    "options": "Form",
                    "hidden": 1,
                    "read_only": 1,
                    "no_copy": 1,
                })
                doctype_doc.save(ignore_permissions=True)
                frappe.clear_cache(doctype=linked_doctype)
                # Reload meta to get the new field
                meta = frappe.get_meta(linked_doctype)
            # Now set the field value
            if meta.has_field(form_tracking_field):
                submission.set(form_tracking_field, form_id)
        except Exception:
            # If adding the field fails, continue without tracking
            # This allows submissions to work even if we can't track them
            pass
    
    # Process form data
    for data in form_data:
        fieldname = data.get("fieldname")
        value = data.get("value", "")
        
        if not fieldname:
            continue
        
        df = meta.get_field(fieldname)
        
        # Handle file uploads, images, and signatures
        # Note: "Image" field type maps to "Attach Image" in Frappe, so we check for both
        if df and df.fieldtype in ("Attach", "Attach Image", "Signature", "Image"):
            # Check if this is a base64 encoded file or signature
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


@frappe.whitelist()
def get_all_submissions() -> list[dict]:
    """Get all forms with their submissions and list view fields"""
    user = frappe.session.user
    
    # Get all forms owned by the user
    forms = frappe.get_all(
        "Form",
        filters={"owner": user},
        fields=["name", "title", "linked_doctype", "route"],
        order_by="title ASC"
    )
    
    result = []
    
    for form in forms:
        linked_doctype = form.linked_doctype
        if not linked_doctype:
            continue
        
        # Get DocType metadata to find list view fields
        try:
            meta = frappe.get_meta(linked_doctype)
            list_view_fields = [
                {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                }
                for field in meta.fields
                if field.in_list_view
            ]
            
            # Always include 'name' field if not already present
            if not any(f["fieldname"] == "name" for f in list_view_fields):
                list_view_fields.insert(0, {
                    "fieldname": "name",
                    "label": "ID",
                    "fieldtype": "Data",
                })
            
            # Get submissions for this specific form
            # Filter by forms_pro_form_id field if it exists
            form_tracking_field = "forms_pro_form_id"
            submissions = []
            
            # Check if the DocType has the tracking field
            if meta.has_field(form_tracking_field):
                # First, get submissions that are explicitly tracked to this form
                tracked_submissions = frappe.get_all(
                    linked_doctype,
                    fields=[f["fieldname"] for f in list_view_fields] + ["creation", "modified", "owner", form_tracking_field],
                    filters={form_tracking_field: form.name},
                    order_by="creation DESC",
                    limit=1000
                )
                submissions.extend(tracked_submissions)
                
                # Check if there are multiple forms using this DocType
                forms_using_doctype = frappe.get_all(
                    "Form",
                    filters={"linked_doctype": linked_doctype, "owner": user},
                    fields=["name"],
                    limit=1000
                )
                
                # If only one form uses this DocType, also include submissions with None form_id
                # (legacy submissions created before tracking was implemented)
                if len(forms_using_doctype) == 1:
                    legacy_submissions = frappe.get_all(
                        linked_doctype,
                        fields=[f["fieldname"] for f in list_view_fields] + ["creation", "modified", "owner", form_tracking_field],
                        filters={form_tracking_field: ["is", "not set"]},
                        order_by="creation DESC",
                        limit=1000
                    )
                    submissions.extend(legacy_submissions)
                
                # Remove form_tracking_field from the result (not needed in list view)
                for sub in submissions:
                    if form_tracking_field in sub:
                        del sub[form_tracking_field]
                
                # Sort by creation date (most recent first)
                submissions.sort(key=lambda x: x.get("creation", ""), reverse=True)
            else:
                # If tracking field doesn't exist, get all documents (fallback)
                # This shouldn't happen in normal operation, but handle it gracefully
                submissions = frappe.get_all(
                    linked_doctype,
                    fields=[f["fieldname"] for f in list_view_fields] + ["creation", "modified", "owner"],
                    order_by="creation DESC",
                    limit=1000
                )
            
            result.append({
                "form": form,
                "submissions": submissions,
                "list_view_fields": list_view_fields,
            })
        except Exception:
            # Skip if doctype doesn't exist or has errors
            continue
    
    return result


@frappe.whitelist()
def get_submission_details(form_id: str, submission_id: str, doctype: str) -> dict:
    """Get full submission document details"""
    # Verify the form exists and user has access
    form = frappe.get_doc("Form", form_id)
    if form.owner != frappe.session.user:
        frappe.throw(_("You don't have permission to view this submission"), frappe.PermissionError)
    
    # Verify the doctype matches the form's linked doctype
    if form.linked_doctype != doctype:
        frappe.throw(_("Invalid submission"), frappe.ValidationError)
    
    # Get the submission document
    try:
        submission = frappe.get_doc(doctype, submission_id)
        # Convert to dict with all fields
        return submission.as_dict()
    except frappe.DoesNotExistError:
        frappe.throw(_("Submission not found"), frappe.DoesNotExistError)


@frappe.whitelist()
def delete_submission(form_id: str, submission_id: str, doctype: str) -> dict:
    """Delete a submission document"""
    # Verify the form exists and user has access
    form = frappe.get_doc("Form", form_id)
    if form.owner != frappe.session.user:
        frappe.throw(_("You don't have permission to delete this submission"), frappe.PermissionError)
    
    # Verify the doctype matches the form's linked doctype
    if form.linked_doctype != doctype:
        frappe.throw(_("Invalid submission"), frappe.ValidationError)
    
    # Delete the submission document
    try:
        frappe.delete_doc(doctype, submission_id, force=True)
        return {"message": _("Submission deleted successfully")}
    except frappe.DoesNotExistError:
        frappe.throw(_("Submission not found"), frappe.DoesNotExistError)
