from datetime import datetime
from typing import Any

import frappe
from pydantic import BaseModel, Field, field_validator

from forms_pro.utils.form_generator import SubmissionStatus


class UserSubmissionResponse(BaseModel):
    name: str = Field(description="Name of the submission")
    creation: datetime = Field(description="Creation date of the submission")
    modified: datetime = Field(description="Last modified date of the submission")
    submission_status: str = Field(
        description="Status of the submission",
        alias="fp_submission_status",
        default=SubmissionStatus.SUBMITTED.value,
    )
    owner: str = Field(description="Owner of the submission")

    @field_validator("creation", "modified", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Convert datetime string to datetime object."""
        if isinstance(v, str):
            return frappe.utils.get_datetime(v)
        if isinstance(v, datetime):
            return v
        raise ValueError(f"Invalid datetime value: {v}")
