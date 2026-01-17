"""SQLAlchemy models for payment tracking and DMO reporting."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from ..database import Base


class Payment(Base):
    """
    Payment record for a bond subscription application.

    Tracks payment received from subscriber including the critical
    deposit/transfer reference needed for DMO fund reconciliation.
    """

    __tablename__ = "payments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Link to application (one payment per application)
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Payment details
    amount = Column(Integer, nullable=False)  # Amount in kobo for precision
    payment_method = Column(String(20), nullable=False)
    payment_reference = Column(String(100), nullable=False)  # Critical for DMO
    payment_date = Column(String(30), nullable=False)
    receiving_bank = Column(String(100))  # Bank that received the payment

    # Status workflow: pending -> verified -> (or rejected)
    status = Column(String(20), nullable=False, default="pending")
    verified_at = Column(String(30))
    verified_by = Column(String(100))  # Admin username who verified
    rejection_reason = Column(Text)

    # Additional info
    notes = Column(Text)

    # Timestamps
    created_at = Column(String(30), default=lambda: datetime.now().isoformat())
    updated_at = Column(String(30))

    # Relationships
    application = relationship("Application", back_populates="payment")
    documents = relationship(
        "PaymentDocument",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "payment_method IN ('bank_transfer', 'cheque', 'cash', 'pos', 'other')",
            name="valid_payment_method",
        ),
        CheckConstraint(
            "status IN ('pending', 'verified', 'rejected')",
            name="valid_payment_status",
        ),
        CheckConstraint("amount > 0", name="positive_amount"),
        Index("idx_payment_record_status", "status"),
        Index("idx_payment_date", "payment_date"),
        Index("idx_payment_reference", "payment_reference"),
    )

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, app_id={self.application_id}, "
            f"ref={self.payment_reference}, status={self.status})>"
        )


class PaymentDocument(Base):
    """
    Payment evidence document (teller copy, transfer receipt, etc.).

    Multiple documents can be attached to a single payment.
    """

    __tablename__ = "payment_documents"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Link to payment
    payment_id = Column(
        Integer,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # File info
    filename = Column(String(255), nullable=False)  # UUID-based stored filename
    original_filename = Column(String(255), nullable=False)  # Original upload name
    file_path = Column(String(500), nullable=False)  # Full path on disk
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))

    # Timestamps
    uploaded_at = Column(String(30), default=lambda: datetime.now().isoformat())

    # Relationships
    payment = relationship("Payment", back_populates="documents")

    __table_args__ = (Index("idx_document_payment", "payment_id"),)

    def __repr__(self) -> str:
        return f"<PaymentDocument(id={self.id}, name={self.original_filename})>"


class DMOSubmission(Base):
    """
    DMO report submission audit trail.

    Tracks when reports are generated and marked as submitted to DMO
    for a specific month of offer.
    """

    __tablename__ = "dmo_submissions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Submission period
    month_of_offer = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)

    # Summary stats at time of submission
    total_applications = Column(Integer, nullable=False)
    total_value = Column(Integer, nullable=False)  # Total in kobo
    total_2year = Column(Integer, default=0)
    total_3year = Column(Integer, default=0)
    total_verified = Column(Integer, default=0)

    # Submission details
    submitted_at = Column(String(30), default=lambda: datetime.now().isoformat())
    submitted_by = Column(String(100))  # Admin username
    report_file_path = Column(String(500))  # Path to generated report file
    notes = Column(Text)

    # Relationships
    applications = relationship("Application", back_populates="dmo_submission")

    __table_args__ = (
        UniqueConstraint("month_of_offer", "year", name="unique_submission_period"),
        Index("idx_submission_period", "month_of_offer", "year"),
    )

    def __repr__(self) -> str:
        return (
            f"<DMOSubmission(id={self.id}, period={self.month_of_offer} {self.year}, "
            f"apps={self.total_applications})>"
        )
