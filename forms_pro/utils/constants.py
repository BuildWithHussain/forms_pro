from forms_pro.utils.form_generator import LINKED_FORM_FIELDOPTIONS, SUBMISSION_STATUS_FIELDOPTIONS

# Frappe fieldtypes that have no Forms Pro equivalent and must be excluded
# when importing fields from an existing DocType into a form.
# These are layout/structural types (Section Break, Column Break, etc.)
# or types with no meaningful input representation (Button, Barcode, Fold).
UNSUPPORTED_FRAPPE_FIELDTYPES: frozenset[str] = frozenset(
    [
        "Section Break",
        "Column Break",
        "Tab Break",
        "Fold",
        "HTML",
        "Button",
        "Barcode",
        "Dynamic Link",
    ]
)

# Fieldnames injected by Forms Pro itself — must never appear in the
# user-visible field list returned to the form builder or submission page.
FORMS_PRO_SYSTEM_FIELDNAMES: frozenset[str] = frozenset(
    [
        SUBMISSION_STATUS_FIELDOPTIONS["fieldname"],  # fp_submission_status
        LINKED_FORM_FIELDOPTIONS["fieldname"],  # fp_linked_form
    ]
)
