import frappe


def execute():
    """
    Backfill row_index / column_index on existing FormField records.
    Each field becomes its own single-column row, preserving vertical order.
    Uses direct SQL to avoid triggering Form.on_update / set_doctype_fields().
    Idempotent: WHERE clause skips already-correct rows.
    """
    frappe.db.sql("""
        UPDATE `tabForm Field`
        SET row_index = idx - 1, column_index = 0
        WHERE row_index != idx - 1 OR column_index != 0
    """)
