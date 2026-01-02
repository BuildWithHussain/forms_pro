import frappe
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo


@frappe.whitelist(allow_guest=True)
def get_brand_logo() -> str:
    """
    Get the brand logo for the form.

    Returns:
        str: The brand logo of the website or the default app logo if brand logo is not set.
    """
    return str(get_app_logo())
