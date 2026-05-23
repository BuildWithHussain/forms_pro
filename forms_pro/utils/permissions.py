import functools
from collections.abc import Callable

import frappe
from frappe import _


def require_permission(doctype: str, ptype: str = "read", param: str = "name") -> Callable:
    """Enforce frappe.has_permission(doctype, ptype, kwargs[param]) before fn runs.

    Raises:
        frappe.DoesNotExistError (HTTP 404): when ptype != "create" and the
            referenced document does not exist.
        frappe.PermissionError (HTTP 403): when the user lacks the permission.

    Args:
        doctype: DocType to check against.
        ptype:   Permission type ("read", "write", "share", "delete", "create").
        param:   Keyword-argument name carrying the docname. Ignored for "create".
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(**kwargs):
            doc_name = kwargs.get(param) if ptype != "create" else None

            if ptype != "create" and doc_name and not frappe.db.exists(doctype, doc_name):
                frappe.throw(
                    _("{0} {1} not found").format(_(doctype), doc_name),
                    frappe.DoesNotExistError,
                    title=_("Not Found"),
                )

            allowed = frappe.has_permission(doctype=doctype, ptype=ptype, doc=doc_name)
            if not allowed:
                frappe.throw(
                    _("You do not have {0} permission on {1}").format(_(ptype), _(doctype)),
                    frappe.PermissionError,
                    title=_("Access Denied"),
                )

            return fn(**kwargs)

        return wrapper

    return decorator
