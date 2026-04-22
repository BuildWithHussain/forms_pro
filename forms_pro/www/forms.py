import re

import frappe

no_cache = 1

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()  # nosemgrep: frappe-semgrep-rules.rules.frappe-manual-commit - required to persist CSRF token before page render
    # developer mode
    context.is_developer_mode = frappe.conf.developer_mode
    context.csrf_token = csrf_token
