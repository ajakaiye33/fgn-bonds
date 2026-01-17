"""SQLAlchemy model for bond subscription applications."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Application(Base):
    """
    FGN Savings Bond subscription application model.

    Stores all ~70 fields for Individual, Joint, and Corporate applicant types.
    """

    __tablename__ = "applications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Submission metadata
    submission_date = Column(String(30), nullable=False)
    created_at = Column(String(30), default=lambda: datetime.now().isoformat())

    # Bond details
    tenor = Column(String(10), nullable=False)  # "2-Year" or "3-Year"
    month_of_offer = Column(String(20), nullable=False)
    bond_value = Column(Integer, nullable=False)  # Store as kobo/integer for precision
    amount_in_words = Column(Text, nullable=False)

    # Applicant type
    applicant_type = Column(String(20), nullable=False)  # Individual, Joint, Corporate

    # Individual/Joint applicant fields (Primary applicant)
    title = Column(String(20))
    full_name = Column(String(200))
    date_of_birth = Column(String(20))
    phone_number = Column(String(20))
    email = Column(String(100))
    occupation = Column(String(100))
    passport_no = Column(String(50))
    next_of_kin = Column(String(200))
    mothers_maiden_name = Column(String(200))
    address = Column(Text)
    cscs_number = Column(String(20))
    chn_number = Column(String(20))

    # Joint applicant fields (Secondary applicant)
    joint_title = Column(String(20))
    joint_full_name = Column(String(200))
    joint_date_of_birth = Column(String(20))
    joint_phone_number = Column(String(20))
    joint_email = Column(String(100))
    joint_occupation = Column(String(100))
    joint_passport_no = Column(String(50))
    joint_next_of_kin = Column(String(200))
    joint_address = Column(Text)

    # Corporate applicant fields
    company_name = Column(String(200))
    rc_number = Column(String(50))
    business_type = Column(String(100))
    contact_person = Column(String(200))
    corp_phone_number = Column(String(20))
    corp_email = Column(String(100))
    corp_passport_no = Column(String(50))

    # Bank details (Primary applicant)
    bank_name = Column(String(100), nullable=False)
    bank_branch = Column(String(200))
    account_number = Column(String(10), nullable=False)
    sort_code = Column(String(20))
    bvn = Column(String(11))

    # Joint applicant bank details
    joint_bank_name = Column(String(100))
    joint_bank_branch = Column(String(200))
    joint_account_number = Column(String(10))
    joint_sort_code = Column(String(20))
    joint_bvn = Column(String(11))

    # Classification
    is_resident = Column(Integer, nullable=False, default=1)  # 1=Resident, 0=Non-Resident
    investor_category = Column(Text)  # JSON array stored as text

    # Distribution agent
    agent_name = Column(String(200))
    stockbroker_code = Column(String(50))

    # Witness section (for illiterate applicants)
    needs_witness = Column(Integer, default=0)  # 0=No, 1=Yes
    witness_name = Column(String(200))
    witness_address = Column(Text)
    witness_acknowledged = Column(Integer, default=0)

    # Payment tracking
    payment_status = Column(String(20), default="pending")  # pending, paid, verified, rejected
    dmo_submission_id = Column(
        Integer,
        ForeignKey("dmo_submissions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    payment = relationship(
        "Payment",
        back_populates="application",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan",
    )
    dmo_submission = relationship("DMOSubmission", back_populates="applications")

    # Table constraints
    __table_args__ = (
        CheckConstraint("tenor IN ('2-Year', '3-Year')", name="valid_tenor"),
        CheckConstraint(
            "applicant_type IN ('Individual', 'Joint', 'Corporate')",
            name="valid_applicant_type",
        ),
        CheckConstraint(
            "bond_value >= 5000 AND bond_value <= 50000000", name="valid_bond_value"
        ),
        CheckConstraint("length(account_number) = 10", name="valid_account_number"),
        CheckConstraint(
            "bvn IS NULL OR length(bvn) = 11", name="valid_bvn"
        ),
        CheckConstraint("is_resident IN (0, 1)", name="valid_is_resident"),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'verified', 'rejected')",
            name="valid_payment_status",
        ),
        # Indexes for common queries
        Index("idx_applicant_type", "applicant_type"),
        Index("idx_submission_date", "submission_date"),
        Index("idx_month_of_offer", "month_of_offer"),
        Index("idx_tenor", "tenor"),
        Index("idx_payment_status", "payment_status"),
    )

    def __repr__(self) -> str:
        if self.applicant_type == "Corporate":
            name = self.company_name
        else:
            name = self.full_name
        return f"<Application(id={self.id}, type={self.applicant_type}, name={name})>"
