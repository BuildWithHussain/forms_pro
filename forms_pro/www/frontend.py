import frappe
from frappe.integrations.frappe_providers.frappecloud_billing import is_fc_site
from frappe.utils.telemetry import capture

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context.csrf_token = csrf_token
	context.site_name = frappe.local.site
	# developer mode
	context.is_developer_mode = frappe.conf.developer_mode
