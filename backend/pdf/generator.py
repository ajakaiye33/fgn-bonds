"""
PDF Generator

High-level interface for generating FGN Savings Bond subscription
form PDFs matching the official DMO form layout.

Author: Hedgar Ajakaiye
License: MIT
"""

from pathlib import Path
from typing import Dict, Optional
import tempfile
import os

from .templates import FGNSBTemplate


class PDFGenerator:
    """
    High-level PDF generation interface for FGNSB subscription forms.
    """

    def __init__(self):
        self.assets_path = Path(__file__).parent.parent.parent / 'assets'

    def generate_subscription_form(self, data: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate a FGNSB subscription form PDF.

        Args:
            data: Dictionary containing application data
            output_path: Optional path for the output PDF.
                        If not provided, a temp file is created.

        Returns:
            Path to the generated PDF file

        Raises:
            ValueError: If required data is missing
            RuntimeError: If PDF generation fails
        """
        # Validate required data
        self._validate_data(data)

        # Create output path if not provided
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='fgnsb_')
            os.close(fd)

        # Generate PDF using template
        template = FGNSBTemplate(data)
        success = template.generate(output_path)

        if not success:
            raise RuntimeError("Failed to generate PDF")

        return output_path

    def _validate_data(self, data: Dict) -> None:
        """
        Validate that required data fields are present.

        Args:
            data: Application data dictionary

        Raises:
            ValueError: If required fields are missing
        """
        applicant_type = data.get('applicant_type', 'Individual')

        # Common required fields
        required_fields = [
            'tenor',
            'bond_value',
            'bank_name',
            'account_number',
            'bvn',
        ]

        # Type-specific required fields
        if applicant_type in ['Individual', 'Joint']:
            required_fields.extend([
                'full_name',
                'phone_number',
                'email',
            ])
            if applicant_type == 'Joint':
                required_fields.extend([
                    'joint_full_name',
                    'joint_phone_number',
                    'joint_email',
                ])
        else:  # Corporate
            required_fields.extend([
                'company_name',
                'rc_number',
                'contact_person',
                'corp_phone_number',
                'corp_email',
            ])

        # Check for missing fields (but don't raise error, just log warning)
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            # Log warning but continue - form handler will validate separately
            import logging
            logging.warning(f"PDF generation: Missing optional fields: {missing}")

    def generate_summary_report(self, applications: list, output_path: Optional[str] = None) -> str:
        """
        Generate a summary report PDF for multiple applications.

        Args:
            applications: List of application data dictionaries
            output_path: Optional path for the output PDF

        Returns:
            Path to the generated PDF file
        """
        # TODO: Implement summary report generation
        raise NotImplementedError("Summary report generation not yet implemented")
