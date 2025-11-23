# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FPTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from forms_pro.forms_pro.doctype.fp_team_member.fp_team_member import FPTeamMember

        team_name: DF.Data
        users: DF.TableMultiSelect[FPTeamMember]
    # end: auto-generated types

    pass
