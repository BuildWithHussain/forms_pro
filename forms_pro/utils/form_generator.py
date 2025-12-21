import frappe

FORMS_PRO_ROLE = "Forms Pro User"


@frappe.whitelist()
def create_form_with_doctype(team_id: str, doctype: str):
    roles = frappe.get_roles(frappe.session.user)
    if FORMS_PRO_ROLE not in roles:
        frappe.throw("You are not authorized to create a form")

    form_generator = FormGenerator(team_id=team_id, linked_doctype=doctype)
    form_generator.generate()

    return {
        "doctype": form_generator.doctype.name,
        "form_document": form_generator.form_document.name,
    }


@frappe.whitelist()
def create_form(team_id: str):
    roles = frappe.get_roles(frappe.session.user)
    if FORMS_PRO_ROLE not in roles:
        frappe.throw("You are not authorized to create a form")

    form_generator = FormGenerator(team_id=team_id)
    form_generator.generate()

    return {
        "doctype": form_generator.doctype.name,
        "form_document": form_generator.form_document.name,
    }


class FormGenerator:
    def __init__(
        self,
        team_id: str,
        linked_doctype: str | None = None,
    ) -> None:
        self.doctype = None
        self.team_id = team_id
        if linked_doctype:
            self.doctype = frappe.get_doc("DocType", linked_doctype)

    def generate(self) -> None:
        self._initialize_doctype()
        self._initialize_form_document()

    def _initialize_doctype(self) -> None:
        if self.doctype:
            return

        placeholder_doctype = frappe.new_doc("DocType")
        placeholder_doctype.name = self._generate_doctype_name()
        placeholder_doctype.module = "Forms Pro"
        placeholder_doctype.custom = True
        placeholder_doctype.track_changes = True
        placeholder_doctype.track_views = True
        placeholder_doctype.index_web_pages_for_search = False
        placeholder_doctype.insert(ignore_permissions=True)

        self.doctype = placeholder_doctype
        # self.set_placeholder_doctype_fields()

    # def set_placeholder_doctype_fields(self) -> None:
    #     fields = [
    #         {
    #             "label": "Is Form Pro DocType",
    #             "fieldname": "is_forms_pro_doctype",
    #             "fieldtype": "Check",
    #             "reqd": 1,
    #             "read_only": 1,
    #             "default": 1,
    #         }
    #     ]

    #     for field in fields:
    #         self.doctype.append("fields", field)

    #     self.doctype.save(ignore_permissions=True)

    def _initialize_form_document(self) -> None:
        form_document = frappe.new_doc("Form")
        form_document.linked_doctype = self.doctype.name
        form_document.title = "Untitled Form"
        form_document.linked_team_id = self.team_id
        form_document.insert(ignore_permissions=True)
        self.form_document = form_document

    def _generate_doctype_name(self) -> str:
        """
        Generate a unique DocType name with format: formspro_XXXXXX_YYYYYY
        where XXXXXX is a random 6-character string and YYYYYY is a serialized number
        """
        # Count existing formspro_* DocTypes from Forms Pro module
        count = frappe.db.count("DocType", filters={"module": "Forms Pro", "name": ["like", "formspro_%"]})

        # Next number is count + 1
        next_number = count + 1

        # Generate random 6-character string
        random_string = frappe.utils.random_string(6)

        # Format the name with random string and 6-digit padding
        doctype_name = f"formspro_{random_string}{next_number:06d}".lower()

        return doctype_name
