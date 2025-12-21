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

    @property
    def team_members(self) -> list[str]:
        """
        Get the list of team members

        Returns:
            list[str] - List of team member email addresses
        """
        return [member.user for member in self.users] if self.users else []

    def is_team_member(self, user: str) -> bool:
        """
        Check if a user is a member of the team

        Args:
            user: The user email address

        Returns:
            bool - True if the user is a member of the team, False otherwise
        """
        return user in self.team_members
