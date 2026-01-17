"""PDF generation service wrapper."""

import json
import tempfile
from pathlib import Path

import structlog

from ..models.application import Application

# Import the copied PDF generator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "pdf"))
from pdf.generator import PDFGenerator

logger = structlog.get_logger()


def generate_application_pdf(application: Application) -> str:
    """
    Generate a PDF for the given application.

    Args:
        application: The application database model.

    Returns:
        Path to the generated PDF file.

    Raises:
        RuntimeError: If PDF generation fails.
    """
    logger.info("Starting PDF generation", application_id=application.id)

    # Convert application model to dict for PDF generator
    data = {
        "tenor": application.tenor,
        "month_of_offer": application.month_of_offer,
        "bond_value": application.bond_value,
        "amount_in_words": application.amount_in_words,
        "applicant_type": application.applicant_type,
        # Individual/Joint fields
        "title": application.title,
        "full_name": application.full_name,
        "date_of_birth": application.date_of_birth,
        "phone_number": application.phone_number,
        "email": application.email,
        "occupation": application.occupation,
        "passport_no": application.passport_no,
        "next_of_kin": application.next_of_kin,
        "mothers_maiden_name": application.mothers_maiden_name,
        "address": application.address,
        "cscs_number": application.cscs_number,
        "chn_number": application.chn_number,
        # Joint applicant fields
        "joint_title": application.joint_title,
        "joint_full_name": application.joint_full_name,
        "joint_date_of_birth": application.joint_date_of_birth,
        "joint_phone_number": application.joint_phone_number,
        "joint_email": application.joint_email,
        "joint_occupation": application.joint_occupation,
        "joint_passport_no": application.joint_passport_no,
        "joint_next_of_kin": application.joint_next_of_kin,
        "joint_address": application.joint_address,
        # Corporate fields
        "company_name": application.company_name,
        "rc_number": application.rc_number,
        "business_type": application.business_type,
        "contact_person": application.contact_person,
        "corp_phone_number": application.corp_phone_number,
        "corp_email": application.corp_email,
        "corp_passport_no": application.corp_passport_no,
        # Bank details
        "bank_name": application.bank_name,
        "bank_branch": application.bank_branch,
        "account_number": application.account_number,
        "sort_code": application.sort_code,
        "bvn": application.bvn,
        # Joint bank details
        "joint_bank_name": application.joint_bank_name,
        "joint_bank_branch": application.joint_bank_branch,
        "joint_account_number": application.joint_account_number,
        "joint_sort_code": application.joint_sort_code,
        "joint_bvn": application.joint_bvn,
        # Classification
        "is_resident": application.is_resident == 1,
        "investor_category": (
            json.loads(application.investor_category)
            if application.investor_category
            else []
        ),
        # Distribution
        "agent_name": application.agent_name,
        "stockbroker_code": application.stockbroker_code,
        # Witness
        "needs_witness": application.needs_witness == 1,
        "witness_name": application.witness_name,
        "witness_address": application.witness_address,
        "witness_acknowledged": application.witness_acknowledged == 1,
    }

    # Generate PDF to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        output_path = tmp.name

    try:
        generator = PDFGenerator()
        pdf_path = generator.generate_subscription_form(data, output_path)
        logger.info("PDF generated successfully", path=pdf_path)
        return pdf_path
    except Exception as e:
        logger.exception("PDF generation failed", error=str(e))
        raise RuntimeError(f"Failed to generate PDF: {e}")
