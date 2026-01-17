"""Pydantic schemas for payment tracking and DMO reporting."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Payment method options
PaymentMethod = Literal["bank_transfer", "cheque", "cash", "pos", "other"]
PaymentStatus = Literal["pending", "verified", "rejected"]
ApplicationPaymentStatus = Literal["pending", "paid", "verified", "rejected"]


class PaymentCreate(BaseModel):
    """Schema for recording a new payment."""

    amount: float = Field(..., gt=0, description="Payment amount in Naira")
    payment_method: PaymentMethod
    payment_reference: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Deposit/transfer reference number (critical for DMO)",
    )
    payment_date: str = Field(..., description="Date payment was received (YYYY-MM-DD)")
    receiving_bank: str | None = Field(
        None, max_length=100, description="Bank that received the payment"
    )
    notes: str | None = Field(None, description="Additional notes about the payment")

    @field_validator("payment_date", mode="before")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format."""
        if v:
            try:
                # Try parsing the date
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class PaymentUpdate(BaseModel):
    """Schema for updating payment details."""

    amount: float | None = Field(None, gt=0)
    payment_method: PaymentMethod | None = None
    payment_reference: str | None = Field(None, min_length=1, max_length=100)
    payment_date: str | None = None
    receiving_bank: str | None = Field(None, max_length=100)
    notes: str | None = None

    @field_validator("payment_date", mode="before")
    @classmethod
    def validate_date(cls, v: str | None) -> str | None:
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class PaymentVerify(BaseModel):
    """Schema for verifying or rejecting a payment."""

    action: Literal["verify", "reject"]
    rejection_reason: str | None = Field(
        None, description="Required when rejecting a payment"
    )

    def model_post_init(self, __context) -> None:
        """Validate rejection_reason is provided when rejecting."""
        if self.action == "reject" and not self.rejection_reason:
            raise ValueError("Rejection reason is required when rejecting a payment")


class PaymentDocumentResponse(BaseModel):
    """Schema for payment document response."""

    id: int
    payment_id: int
    filename: str
    original_filename: str
    file_size: int | None
    mime_type: str | None
    uploaded_at: str

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    """Schema for payment response."""

    id: int
    application_id: int
    amount: float
    payment_method: str
    payment_reference: str
    payment_date: str
    receiving_bank: str | None
    status: str
    verified_at: str | None
    verified_by: str | None
    rejection_reason: str | None
    notes: str | None
    created_at: str
    updated_at: str | None
    documents: list[PaymentDocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount(cls, v) -> float:
        """Convert amount from kobo (integer) to Naira (float)."""
        if isinstance(v, int):
            return v / 100.0
        return float(v) if v else 0.0


class PaymentSummary(BaseModel):
    """Brief payment info for application list view."""

    id: int
    payment_reference: str
    amount: float
    status: str
    payment_date: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="before")
    @classmethod
    def convert_amount(cls, v) -> float:
        if isinstance(v, int):
            return v / 100.0
        return float(v) if v else 0.0


class DMOSubmissionCreate(BaseModel):
    """Schema for marking applications as submitted to DMO."""

    month_of_offer: str = Field(..., description="Month of offer (e.g., 'January')")
    year: int = Field(..., ge=2020, le=2100)
    notes: str | None = None


class DMOSubmissionResponse(BaseModel):
    """Schema for DMO submission response."""

    id: int
    month_of_offer: str
    year: int
    total_applications: int
    total_value: float  # In Naira
    total_2year: int
    total_3year: int
    total_verified: int
    submitted_at: str
    submitted_by: str | None
    report_file_path: str | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("total_value", mode="before")
    @classmethod
    def convert_value(cls, v) -> float:
        """Convert value from kobo to Naira."""
        if isinstance(v, int):
            return v / 100.0
        return float(v) if v else 0.0


class MonthlyReportSummary(BaseModel):
    """Summary statistics for monthly DMO report."""

    month_of_offer: str
    year: int

    # Totals
    total_applications: int
    total_value: float  # In Naira
    average_value: float

    # By tenor
    total_2year: int
    value_2year: float
    total_3year: int
    value_3year: float

    # By applicant type
    total_individual: int
    total_joint: int
    total_corporate: int

    # By payment status
    pending_count: int
    pending_value: float
    paid_count: int
    paid_value: float
    verified_count: int
    verified_value: float
    rejected_count: int
    rejected_value: float

    # Submission status
    is_submitted: bool = False
    submission_id: int | None = None
    submitted_at: str | None = None


class ApplicationWithPayment(BaseModel):
    """Extended application response including payment info."""

    # Core application fields
    id: int
    submission_date: str
    tenor: str
    month_of_offer: str
    bond_value: float
    applicant_type: str

    # Applicant name (varies by type)
    applicant_name: str

    # Bank details
    bank_name: str
    account_number: str
    bvn: str | None

    # Payment tracking
    payment_status: str
    payment: PaymentSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class ReportExportRequest(BaseModel):
    """Request parameters for exporting DMO report."""

    month_of_offer: str
    year: int
    format: Literal["excel", "pdf", "csv"] = "excel"
    include_pending: bool = False  # Whether to include pending payments
