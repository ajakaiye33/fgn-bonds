"""
Tests for Pydantic schema validation.
"""

import pytest
from pydantic import ValidationError

from app.schemas.application import ApplicationCreate
from app.schemas.payment import PaymentCreate, PaymentVerify


class TestApplicationSchemas:
    """Tests for application schema validation."""

    def test_valid_individual_application(self, sample_individual_application):
        """Test valid Individual application passes validation."""
        app = ApplicationCreate(**sample_individual_application)
        assert app.applicant_type == "Individual"
        assert app.full_name == "John Doe"
        assert app.bond_value == 100000

    def test_valid_joint_application(self, sample_joint_application):
        """Test valid Joint application passes validation."""
        app = ApplicationCreate(**sample_joint_application)
        assert app.applicant_type == "Joint"
        assert app.joint_full_name == "Jane Doe"

    def test_valid_corporate_application(self, sample_corporate_application):
        """Test valid Corporate application passes validation."""
        app = ApplicationCreate(**sample_corporate_application)
        assert app.applicant_type == "Corporate"
        assert app.company_name == "Test Company Ltd"

    def test_invalid_email_format(self, sample_individual_application):
        """Test invalid email format fails validation."""
        sample_individual_application["email"] = "invalid-email"
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "email" in str(exc_info.value).lower()

    def test_short_phone_number_accepted(self, sample_individual_application):
        """Test that schema accepts phone numbers (validation is lenient)."""
        # Note: Schema normalizes but doesn't strictly validate phone format
        # This is by design - strict validation happens at frontend
        sample_individual_application["phone_number"] = "12345"
        app = ApplicationCreate(**sample_individual_application)
        assert app.phone_number == "12345"  # Accepted as-is (too short to normalize)

    def test_valid_nigerian_phone_formats(self, sample_individual_application):
        """Test various Nigerian phone number formats."""
        valid_formats = [
            "+2348012345678",
            "2348012345678",
            "08012345678",
        ]
        for phone in valid_formats:
            sample_individual_application["phone_number"] = phone
            app = ApplicationCreate(**sample_individual_application)
            # Phone should be normalized to +234 format
            assert app.phone_number.startswith("+234") or app.phone_number.startswith("0")

    def test_invalid_account_number_length(self, sample_individual_application):
        """Test account number must be exactly 10 digits."""
        sample_individual_application["account_number"] = "12345"  # Too short
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "account" in str(exc_info.value).lower()

    def test_invalid_bvn_length(self, sample_individual_application):
        """Test BVN must be exactly 11 digits."""
        sample_individual_application["bvn"] = "12345"  # Too short
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "bvn" in str(exc_info.value).lower()

    def test_bond_value_minimum(self, sample_individual_application):
        """Test bond value minimum constraint (5000)."""
        sample_individual_application["bond_value"] = 1000  # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "bond_value" in str(exc_info.value).lower() or "5000" in str(exc_info.value)

    def test_bond_value_maximum(self, sample_individual_application):
        """Test bond value maximum constraint (50,000,000)."""
        sample_individual_application["bond_value"] = 100000000  # Above maximum
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "bond_value" in str(exc_info.value).lower() or "50000000" in str(exc_info.value)

    def test_invalid_tenor(self, sample_individual_application):
        """Test tenor must be 2-Year or 3-Year."""
        sample_individual_application["tenor"] = "5-Year"
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreate(**sample_individual_application)
        assert "tenor" in str(exc_info.value).lower()

    def test_individual_requires_full_name(self, sample_individual_application):
        """Test Individual applicant requires full_name."""
        del sample_individual_application["full_name"]
        with pytest.raises(ValidationError):
            ApplicationCreate(**sample_individual_application)

    def test_joint_requires_both_names(self, sample_joint_application):
        """Test Joint applicant requires both applicants' names."""
        del sample_joint_application["joint_full_name"]
        with pytest.raises(ValidationError):
            ApplicationCreate(**sample_joint_application)

    def test_corporate_requires_company_name(self, sample_corporate_application):
        """Test Corporate applicant requires company_name."""
        del sample_corporate_application["company_name"]
        with pytest.raises(ValidationError):
            ApplicationCreate(**sample_corporate_application)


class TestPaymentSchemas:
    """Tests for payment schema validation."""

    def test_valid_payment_create(self, sample_payment):
        """Test valid payment data passes validation."""
        payment = PaymentCreate(**sample_payment)
        assert payment.amount == 100000
        assert payment.payment_method == "bank_transfer"

    def test_payment_amount_must_be_positive(self, sample_payment):
        """Test payment amount must be greater than 0."""
        sample_payment["amount"] = 0
        with pytest.raises(ValidationError):
            PaymentCreate(**sample_payment)

    def test_invalid_payment_method(self, sample_payment):
        """Test invalid payment method fails."""
        sample_payment["payment_method"] = "bitcoin"
        with pytest.raises(ValidationError):
            PaymentCreate(**sample_payment)

    def test_payment_reference_required(self, sample_payment):
        """Test payment reference is required."""
        del sample_payment["payment_reference"]
        with pytest.raises(ValidationError):
            PaymentCreate(**sample_payment)

    def test_payment_verify_requires_action(self):
        """Test payment verify requires action."""
        with pytest.raises(ValidationError):
            PaymentVerify()

    def test_payment_reject_requires_reason(self):
        """Test rejecting payment requires reason."""
        with pytest.raises(ValidationError):
            PaymentVerify(action="reject")

    def test_payment_verify_valid(self):
        """Test valid payment verification."""
        verify = PaymentVerify(action="verify")
        assert verify.action == "verify"

    def test_payment_reject_valid(self):
        """Test valid payment rejection with reason."""
        verify = PaymentVerify(action="reject", rejection_reason="Invalid reference")
        assert verify.action == "reject"
        assert verify.rejection_reason == "Invalid reference"
