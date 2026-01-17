"""Pydantic schemas for application request/response validation."""

import json
import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..utils.constants import BOND_VALUE_MAX, BOND_VALUE_MIN


class ApplicationBase(BaseModel):
    """Base schema with common application fields."""

    # Bond details
    tenor: Literal["2-Year", "3-Year"]
    month_of_offer: str = Field(..., min_length=1, max_length=20)
    bond_value: float = Field(..., ge=BOND_VALUE_MIN, le=BOND_VALUE_MAX)
    amount_in_words: str = Field(..., min_length=1)

    # Applicant type
    applicant_type: Literal["Individual", "Joint", "Corporate"]

    # Individual/Joint applicant fields (Primary applicant)
    title: str | None = None
    full_name: str | None = None
    date_of_birth: str | None = None
    phone_number: str | None = None
    email: str | None = None
    occupation: str | None = None
    passport_no: str | None = None
    next_of_kin: str | None = None
    mothers_maiden_name: str | None = None
    address: str | None = None
    cscs_number: str | None = None
    chn_number: str | None = None

    # Joint applicant fields (Secondary applicant)
    joint_title: str | None = None
    joint_full_name: str | None = None
    joint_date_of_birth: str | None = None
    joint_phone_number: str | None = None
    joint_email: str | None = None
    joint_occupation: str | None = None
    joint_passport_no: str | None = None
    joint_next_of_kin: str | None = None
    joint_address: str | None = None

    # Corporate applicant fields
    company_name: str | None = None
    rc_number: str | None = None
    business_type: str | None = None
    contact_person: str | None = None
    corp_phone_number: str | None = None
    corp_email: str | None = None
    corp_passport_no: str | None = None

    # Bank details (Primary applicant)
    bank_name: str = Field(..., min_length=1)
    bank_branch: str | None = None
    account_number: str = Field(..., min_length=10, max_length=10)
    sort_code: str | None = None
    bvn: str | None = Field(None, min_length=11, max_length=11)

    # Joint applicant bank details
    joint_bank_name: str | None = None
    joint_bank_branch: str | None = None
    joint_account_number: str | None = Field(None, min_length=10, max_length=10)
    joint_sort_code: str | None = None
    joint_bvn: str | None = Field(None, min_length=11, max_length=11)

    # Classification
    is_resident: bool = True
    investor_category: list[str] | None = None

    # Distribution agent
    agent_name: str | None = None
    stockbroker_code: str | None = None

    # Witness section
    needs_witness: bool = False
    witness_name: str | None = None
    witness_address: str | None = None
    witness_acknowledged: bool = False

    @field_validator("email", "joint_email", "corp_email", mode="before")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("phone_number", "joint_phone_number", "corp_phone_number", mode="before")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # Remove non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", v)
        # Normalize Nigerian phone numbers
        if cleaned.startswith("0"):
            cleaned = "+234" + cleaned[1:]
        elif cleaned.startswith("234"):
            cleaned = "+" + cleaned
        return cleaned

    @field_validator("account_number", "joint_account_number", mode="before")
    @classmethod
    def validate_account_number(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # Must be exactly 10 digits
        if not re.match(r"^\d{10}$", v):
            raise ValueError("Account number must be exactly 10 digits")
        return v

    @field_validator("bvn", "joint_bvn", mode="before")
    @classmethod
    def validate_bvn(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # Must be exactly 11 digits
        if not re.match(r"^\d{11}$", v):
            raise ValueError("BVN must be exactly 11 digits")
        return v

    @model_validator(mode="after")
    def validate_applicant_type_fields(self):
        """Validate required fields based on applicant type."""
        if self.applicant_type == "Individual":
            if not self.full_name:
                raise ValueError("Full name is required for Individual applicants")
            if not self.phone_number:
                raise ValueError("Phone number is required for Individual applicants")

        elif self.applicant_type == "Joint":
            if not self.full_name:
                raise ValueError("Primary applicant full name is required for Joint applications")
            if not self.joint_full_name:
                raise ValueError("Joint applicant full name is required for Joint applications")

        elif self.applicant_type == "Corporate":
            if not self.company_name:
                raise ValueError("Company name is required for Corporate applicants")
            if not self.rc_number:
                raise ValueError("RC number is required for Corporate applicants")
            if not self.contact_person:
                raise ValueError("Contact person is required for Corporate applicants")

        return self


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application."""

    submission_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S WAT")
    )

    def model_dump(self, **kwargs):
        """Convert to dict for database storage."""
        data = super().model_dump(**kwargs)
        # Convert boolean to integer for SQLite
        data["is_resident"] = 1 if data["is_resident"] else 0
        data["needs_witness"] = 1 if data["needs_witness"] else 0
        data["witness_acknowledged"] = 1 if data["witness_acknowledged"] else 0
        # Convert investor_category list to JSON string
        if data["investor_category"]:
            data["investor_category"] = json.dumps(data["investor_category"])
        return data


class ApplicationResponse(BaseModel):
    """Schema for application response."""

    id: int
    submission_date: str
    created_at: str | None = None

    # Bond details
    tenor: str
    month_of_offer: str
    bond_value: float
    amount_in_words: str

    # Applicant type
    applicant_type: str

    # Individual/Joint applicant fields
    title: str | None = None
    full_name: str | None = None
    date_of_birth: str | None = None
    phone_number: str | None = None
    email: str | None = None
    occupation: str | None = None
    passport_no: str | None = None
    next_of_kin: str | None = None
    mothers_maiden_name: str | None = None
    address: str | None = None
    cscs_number: str | None = None
    chn_number: str | None = None

    # Joint applicant fields
    joint_title: str | None = None
    joint_full_name: str | None = None
    joint_date_of_birth: str | None = None
    joint_phone_number: str | None = None
    joint_email: str | None = None
    joint_occupation: str | None = None
    joint_passport_no: str | None = None
    joint_next_of_kin: str | None = None
    joint_address: str | None = None

    # Corporate applicant fields
    company_name: str | None = None
    rc_number: str | None = None
    business_type: str | None = None
    contact_person: str | None = None
    corp_phone_number: str | None = None
    corp_email: str | None = None
    corp_passport_no: str | None = None

    # Bank details
    bank_name: str
    bank_branch: str | None = None
    account_number: str
    sort_code: str | None = None
    bvn: str | None = None

    # Joint bank details
    joint_bank_name: str | None = None
    joint_bank_branch: str | None = None
    joint_account_number: str | None = None
    joint_sort_code: str | None = None
    joint_bvn: str | None = None

    # Classification
    is_resident: bool
    investor_category: list[str] | None = None

    # Distribution
    agent_name: str | None = None
    stockbroker_code: str | None = None

    # Witness
    needs_witness: bool = False
    witness_name: str | None = None
    witness_address: str | None = None
    witness_acknowledged: bool = False

    # Payment tracking
    payment_status: str = "pending"

    model_config = ConfigDict(from_attributes=True)

    @field_validator("is_resident", mode="before")
    @classmethod
    def convert_is_resident(cls, v) -> bool:
        if isinstance(v, int):
            return v == 1
        return bool(v)

    @field_validator("needs_witness", "witness_acknowledged", mode="before")
    @classmethod
    def convert_bool_fields(cls, v) -> bool:
        if isinstance(v, int):
            return v == 1
        return bool(v) if v else False

    @field_validator("investor_category", mode="before")
    @classmethod
    def parse_investor_category(cls, v) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v
