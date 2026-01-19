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


@frappe.whitelist(allow_guest=True)
def get_website_settings() -> dict:
    website_settings = frappe.get_doc("Website Settings")
    form_settings = {
        "disable_sign_up": website_settings.disable_signup,
    }
    return form_settings
