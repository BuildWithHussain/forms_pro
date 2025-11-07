import frappe

no_cache = 1


def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    # developer mode
    context.is_developer_mode = frappe.conf.developer_mode

    if frappe.session.user == "Guest":
        boot = frappe.website.utils.get_boot_data()
    else:
        try:
            boot = frappe.sessions.get()
        except Exception as e:
            raise frappe.SessionBootFailed from e

    # Serialize boot data using frappe.as_json which handles datetime objects
    # and other non-standard JSON types properly
    boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))

    context.update(
        {
            "build_version": frappe.utils.get_build_version(),
            "boot": boot_json,
            "csrf_token": csrf_token,
            "site_name": frappe.local.site,
        }
    )
