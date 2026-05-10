import frappe


def execute():
    """
    Backfill row_index / column_index on existing FormField records.
    Each field becomes its own single-column row, preserving vertical order.
    Uses direct SQL to avoid triggering Form.on_update / set_doctype_fields().
    Idempotent: WHERE clause skips already-correct rows.
    """
    # row_index / column_index on `tabForm Field` are Int NOT NULL DEFAULT 0
    # (Frappe's schema sync). Legacy rows pre-dating these columns therefore
    # land on 0 after migration, not NULL — so a plain `!=` predicate is
    # enough. No IS NULL branch needed.
    frappe.db.sql("""
        UPDATE `tabForm Field`
        SET row_index = idx - 1, column_index = 0
        WHERE row_index != idx - 1 OR column_index != 0
    """)
