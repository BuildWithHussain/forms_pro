# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.share import add_docshare
from pydantic import BaseModel, EmailStr

from forms_pro.api.user import get_user
from forms_pro.utils.teams import set_current_team


class GetTeamMembersResponse(BaseModel):
    full_name: str
    user_image: str | None
    email: EmailStr


class FPTeam(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from forms_pro.forms_pro.doctype.fp_team_member.fp_team_member import FPTeamMember

        logo: DF.AttachImage | None
        team_name: DF.Data
        users: DF.TableMultiSelect[FPTeamMember]
    # end: auto-generated types

    @property
    def team_members(self) -> list[GetTeamMembersResponse]:
        """
        Get the list of team members

        Returns:
            list[str] - List of team member email addresses
        """
        if not len(self.users):
            return []

        members = []

        for member in self.users:
            _user = get_user(member.user)
            _user["email"] = member.user
            members.append(GetTeamMembersResponse.model_validate(_user).model_dump())

        return members

    def is_team_member(self, user: str) -> bool:
        """
        Check if a user is a member of the team

        Args:
            user: The user email address

        Returns:
            bool - True if the user is a member of the team, False otherwise
        """
        return user in [member["email"] for member in self.team_members]

    def after_insert(self) -> None:
        self.add_to_team(self.owner)
        set_current_team(self.name, self.owner)
        self.save()

    def add_to_team(self, user: str) -> None:
        """
        Add a user to the team

        Args:
            user: The user email address
        """
        if user == "Administrator":
            return

        if self.is_team_member(user):
            frappe.throw(
                frappe._("User is already a member of the team"),
                frappe.DuplicateEntryError,
            )

        self.append("users", {"user": user})
        add_docshare(
            self.doctype,
            self.name,
            user,
            read=1,
            write=1,
            share=1,
            flags={"ignore_share_permission": True},
        )
