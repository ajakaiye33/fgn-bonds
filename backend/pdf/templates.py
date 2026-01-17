"""
PDF Templates

Main template for generating the official DMO FGNSB subscription form PDF.
Matches the official Debt Management Office form layout with green color scheme.

Author: Hedgar Ajakaiye
License: MIT
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from datetime import datetime
from typing import Dict, Optional
import os
from pathlib import Path

from .styles import PDFColors, PDFStyles
from .elements import (
    CheckboxField, CheckboxGroup, InputBoxes, PhoneInputBoxes,
    SignatureLine, StampArea, SectionHeader, ThumbprintArea, DottedInputLine
)


class FGNSBTemplate:
    """
    Template for generating FGNSB subscription form matching official DMO styling.
    """

    def __init__(self, data: Dict):
        self.data = data
        self.width, self.height = A4
        self.margin = PDFStyles.PAGE_MARGIN
        self.content_width = self.width - (2 * self.margin)

        # Get logo path - pdf module is at /app/pdf/, so parent.parent gives /app
        self.assets_path = Path(__file__).parent.parent / 'assets'
        self.logo_path = self.assets_path / 'dmo_logo.png'

    def _build_header(self) -> list:
        """Build the document header with DMO logo and addressing"""
        elements = []

        # Create header table with To/Logo/No sections
        header_data = []

        # Top row with addressing and logo
        to_text = Paragraph(
            "<b>To:</b><br/>Director-General,<br/>Debt Management Office, Abuja",
            ParagraphStyle('To', fontName='Helvetica', fontSize=8, leading=10)
        )

        # Logo in center
        if self.logo_path.exists():
            logo = Image(str(self.logo_path), width=60, height=45)
        else:
            logo = Paragraph(
                "<b>DEBT MANAGEMENT OFFICE<br/>NIGERIA</b>",
                ParagraphStyle('LogoText', fontName='Helvetica-Bold', fontSize=10,
                              alignment=TA_CENTER, leading=12)
            )

        no_text = Paragraph(
            "<b>No:</b> ____________<br/><br/><i>Official use only</i>",
            ParagraphStyle('No', fontName='Helvetica', fontSize=8, alignment=TA_RIGHT, leading=10)
        )

        header_data.append([to_text, logo, no_text])

        header_table = Table(header_data, colWidths=[self.content_width * 0.3,
                                                      self.content_width * 0.4,
                                                      self.content_width * 0.3])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 8))

        # Title
        title_style = ParagraphStyle(
            'Title',
            fontName='Helvetica-Bold',
            fontSize=11,
            alignment=TA_CENTER,
            textColor=PDFColors.BLACK,
            spaceAfter=4,
        )
        elements.append(Paragraph(
            "SUBSCRIPTION FORM FOR FEDERAL GOVERNMENT OF NIGERIA SAVINGS BOND (FGNSB)",
            title_style
        ))

        # Instructions
        instruction_style = ParagraphStyle(
            'Instructions',
            fontName='Helvetica',
            fontSize=7,
            alignment=TA_CENTER,
            textColor=PDFColors.GRAY,
            leading=9,
        )
        elements.append(Paragraph(
            "Applications must be made in accordance with the instructions set out on the back of this application form. "
            "Care must be taken to follow these instructions as applications that do not comply with the instructions may be rejected. "
            "If you are in any doubt, please consult your Stockbroker, Banker, Solicitor, or any professional adviser for guidance.",
            instruction_style
        ))
        elements.append(Spacer(1, 4))

        # Declaration line
        declaration_style = ParagraphStyle(
            'Declaration',
            fontName='Helvetica-Oblique',
            fontSize=8,
            alignment=TA_CENTER,
            textColor=PDFColors.BLACK,
        )
        elements.append(Paragraph(
            "In response to the advertisement in both print and electronic media, I/We hereby offer my/our subscription for FGNSB",
            declaration_style
        ))
        elements.append(Spacer(1, 8))

        return elements

    def _build_section_a(self) -> list:
        """Build Section A: Guide to Applications"""
        elements = []

        # Section header
        elements.append(SectionHeader("A", "Guide to Applications", width=self.content_width))
        elements.append(Spacer(1, 4))

        # Build the guide section content
        tenor = self.data.get('tenor', '2-Year')
        month_of_offer = self.data.get('month_of_offer', '')
        bond_value = self.data.get('bond_value', 0)
        amount_words = self.data.get('amount_in_words', '')

        # Row 1: Tenor and Month
        tenor_2yr = "X" if tenor == "2-Year" else " "
        tenor_3yr = "X" if tenor == "3-Year" else " "

        row1_data = [
            [
                Paragraph("<b>Tenor of Bond:</b>", PDFStyles.get_body_style()),
                Paragraph(f"2-Year [{tenor_2yr}]", PDFStyles.get_body_style()),
                Paragraph(f"3-Year [{tenor_3yr}]", PDFStyles.get_body_style()),
                Paragraph("<b>Month of Offer:</b>", PDFStyles.get_body_style()),
                Paragraph(str(month_of_offer), PDFStyles.get_body_style()),
            ]
        ]
        row1_table = Table(row1_data, colWidths=[80, 70, 70, 80, 100])
        row1_table.setStyle(PDFStyles.get_form_table_style())
        elements.append(row1_table)

        # Row 2: Values section
        row2_data = [
            [
                Paragraph("<b>Minimum Value:</b> N5,000.00", PDFStyles.get_body_style()),
                Paragraph(f"<b>Value of Bonds Applied for:</b> N{bond_value:,.2f}", PDFStyles.get_body_style()),
            ],
            [
                Paragraph("<b>Maximum Value:</b> N50,000,000.00", PDFStyles.get_body_style()),
                Paragraph(f"<b>Amount in Words:</b> {amount_words}", PDFStyles.get_body_style()),
            ]
        ]
        row2_table = Table(row2_data, colWidths=[self.content_width * 0.4, self.content_width * 0.6])
        row2_table.setStyle(PDFStyles.get_form_table_style())
        elements.append(row2_table)

        # E-allotment details
        cscs_number = self.data.get('cscs_number', '')
        chn_number = self.data.get('chn_number', '')

        eallot_data = [
            ["E-allotment Details", ""],
            [Paragraph("<b>Applicant's CSCS A/C No.:</b>", PDFStyles.get_body_style()),
             Paragraph(str(cscs_number), PDFStyles.get_body_style())],
            [Paragraph("<b>Applicant's CHN No.:</b>", PDFStyles.get_body_style()),
             Paragraph(str(chn_number), PDFStyles.get_body_style())],
        ]
        eallot_table = Table(eallot_data, colWidths=[self.content_width * 0.4, self.content_width * 0.6])
        eallot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PDFColors.DMO_GREEN_LIGHT),
            ('SPAN', (0, 0), (-1, 0)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(eallot_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_section_b_individual(self) -> list:
        """Build Section B for Individual/Joint applicants"""
        elements = []

        applicant_type = self.data.get('applicant_type', 'Individual')
        section_title = "1. Individual Applicant Details" if applicant_type == "Individual" else "1. Primary Applicant Details"

        elements.append(SectionHeader("B", section_title, width=self.content_width))
        elements.append(Spacer(1, 4))

        # Individual details
        details_data = [
            ["Title:", self.data.get('title', ''), "Full Name:", self.data.get('full_name', '')],
            ["Date of Birth:", self.data.get('date_of_birth', ''), "Phone Number:", self.data.get('phone_number', '')],
            ["Occupation:", self.data.get('occupation', ''), "Passport No:", self.data.get('passport_no', '')],
            ["Next of Kin:", self.data.get('next_of_kin', ''), "Mother's Maiden Name:", self.data.get('mothers_maiden_name', '')],
            ["Address:", self.data.get('address', ''), "Email:", self.data.get('email', '')],
        ]

        details_table = Table(details_data, colWidths=[70, 130, 80, 130])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
            ('BACKGROUND', (2, 0), (2, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 8))

        # Joint applicant section if applicable
        if applicant_type == "Joint":
            elements.extend(self._build_joint_applicant_section())

        return elements

    def _build_joint_applicant_section(self) -> list:
        """Build joint applicant details section"""
        elements = []

        elements.append(SectionHeader("", "2. Joint Applicant Details", width=self.content_width))
        elements.append(Spacer(1, 4))

        joint_data = [
            ["Title:", self.data.get('joint_title', ''), "Full Name:", self.data.get('joint_full_name', '')],
            ["Phone Number:", self.data.get('joint_phone_number', ''), "Email:", self.data.get('joint_email', '')],
            ["Occupation:", self.data.get('joint_occupation', ''), "Passport No:", self.data.get('joint_passport_no', '')],
            ["Next of Kin:", self.data.get('joint_next_of_kin', ''), "Address:", self.data.get('joint_address', '')],
        ]

        joint_table = Table(joint_data, colWidths=[70, 130, 80, 130])
        joint_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
            ('BACKGROUND', (2, 0), (2, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(joint_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_section_b_corporate(self) -> list:
        """Build Section B for Corporate applicants"""
        elements = []

        elements.append(SectionHeader("B", "Corporate Applicant Details", width=self.content_width))
        elements.append(Spacer(1, 4))

        corp_data = [
            ["Company Name:", self.data.get('company_name', ''), "R/C No:", self.data.get('rc_number', '')],
            ["Type of Business:", self.data.get('business_type', ''), "Passport No:", self.data.get('corp_passport_no', '')],
            ["Contact Person:", self.data.get('contact_person', ''), "Phone No:", self.data.get('corp_phone_number', '')],
            ["Address:", self.data.get('address', ''), "Email:", self.data.get('corp_email', '')],
        ]

        corp_table = Table(corp_data, colWidths=[80, 150, 60, 120])
        corp_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
            ('BACKGROUND', (2, 0), (2, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(corp_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_section_c(self) -> list:
        """Build Section C: Bank Details"""
        elements = []

        elements.append(SectionHeader("C", "Bank Details", width=self.content_width))
        elements.append(Spacer(1, 4))

        bank_data = [
            ["Bank Name:", self.data.get('bank_name', ''), "Bank Branch:", self.data.get('bank_branch', '')],
            ["Account Number:", self.data.get('account_number', ''), "Sort Code:", self.data.get('sort_code', '')],
            ["BVN:", self.data.get('bvn', ''), "", ""],
        ]

        bank_table = Table(bank_data, colWidths=[80, 150, 70, 110])
        bank_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
            ('BACKGROUND', (2, 0), (2, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(bank_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_residency_section(self) -> list:
        """Build Residency Classification section"""
        elements = []

        is_resident = self.data.get('is_resident', True)
        resident_check = "X" if is_resident else " "
        non_resident_check = " " if is_resident else "X"

        residency_style = ParagraphStyle(
            'Residency',
            fontName='Helvetica-Bold',
            fontSize=9,
            alignment=TA_LEFT,
        )

        residency_data = [
            [
                Paragraph("<b>Residency Classification of Applicant (tick the Appropriate box):</b>", residency_style),
                Paragraph(f"Resident [{resident_check}]", PDFStyles.get_body_style()),
                Paragraph(f"Non-Resident [{non_resident_check}]", PDFStyles.get_body_style()),
            ]
        ]

        residency_table = Table(residency_data, colWidths=[250, 80, 80])
        residency_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(residency_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_investor_category_section(self) -> list:
        """Build Investor Category section"""
        elements = []

        investor_categories = self.data.get('investor_category', [])

        # Define all available categories
        all_categories = [
            "Individual", "Insurance", "Corporate", "Others",
            "*Foreign Investor", "Non-Bank Financial Institution",
            "Co-operative Society", "Government Agencies",
            "Staff Scheme", "Micro Finance Bank"
        ]

        category_style = ParagraphStyle(
            'Category',
            fontName='Helvetica-Bold',
            fontSize=9,
            alignment=TA_LEFT,
        )

        # Build header
        header_data = [[Paragraph("<b>Investor Category (tick all that apply):</b>", category_style)]]
        header_table = Table(header_data, colWidths=[self.content_width])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PDFColors.DMO_GREEN_LIGHT),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)

        # Build category checkboxes in 2 columns
        cat_rows = []
        for i in range(0, len(all_categories), 2):
            row = []
            for j in range(2):
                if i + j < len(all_categories):
                    cat = all_categories[i + j]
                    checked = "X" if cat in investor_categories else " "
                    row.append(Paragraph(f"[{checked}] {cat}", PDFStyles.get_body_style()))
                else:
                    row.append("")
            cat_rows.append(row)

        cat_table = Table(cat_rows, colWidths=[self.content_width * 0.5, self.content_width * 0.5])
        cat_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_witness_section(self) -> list:
        """Build Witness Section for illiterate applicants"""
        elements = []

        needs_witness = self.data.get('needs_witness', False)

        if not needs_witness:
            return elements

        elements.append(SectionHeader("", "Witness Section (for applicants who cannot sign)", width=self.content_width))
        elements.append(Spacer(1, 4))

        witness_name = self.data.get('witness_name', '')
        witness_address = self.data.get('witness_address', '')
        witness_acknowledged = self.data.get('witness_acknowledged', False)
        ack_check = "X" if witness_acknowledged else " "

        witness_data = [
            ["Witness Name:", witness_name],
            ["Witness Address:", witness_address],
            ["Acknowledgment:", f"[{ack_check}] I confirm that I have witnessed this application and the thumbprint belongs to the applicant"],
        ]

        witness_table = Table(witness_data, colWidths=[100, self.content_width - 100])
        witness_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(witness_table)

        # Thumbprint area
        thumb_style = ParagraphStyle('Thumb', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)
        thumb_data = [
            [
                Paragraph("Witness Signature: _______________________", thumb_style),
                Paragraph("<b>Applicant's Thumbprint</b><br/><br/><br/><br/><br/>", thumb_style),
            ]
        ]
        thumb_table = Table(thumb_data, colWidths=[self.content_width * 0.5, self.content_width * 0.5])
        thumb_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(thumb_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_section_d(self) -> list:
        """Build Section D: Distribution Agents"""
        elements = []

        elements.append(SectionHeader("D", "Distribution Agents", width=self.content_width))
        elements.append(Spacer(1, 4))

        agent_data = [
            ["Name of Distribution Agent:", self.data.get('agent_name', '')],
            ["Stockbroker Code:", self.data.get('stockbroker_code', '')],
        ]

        agent_table = Table(agent_data, colWidths=[150, 260])
        agent_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),
        ]))
        elements.append(agent_table)
        elements.append(Spacer(1, 8))

        return elements

    def _build_signature_section(self) -> list:
        """Build signature and stamp section"""
        elements = []

        # Create a table with signature lines and stamp area
        sig_style = ParagraphStyle('Sig', fontName='Helvetica', fontSize=8, leading=10)

        sig_data = [
            [
                Paragraph("Usual Signature: _______________________<br/><br/>Date: _______________", sig_style),
                Paragraph("<b>Stamp of Receiving Agent</b>", sig_style),
            ]
        ]

        sig_table = Table(sig_data, colWidths=[self.content_width * 0.5, self.content_width * 0.5])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
        elements.append(sig_table)

        return elements

    def _build_footer(self) -> list:
        """Build document footer with generation timestamp"""
        elements = []
        elements.append(Spacer(1, 12))

        footer_style = ParagraphStyle(
            'Footer',
            fontName='Helvetica',
            fontSize=7,
            textColor=PDFColors.GRAY,
            alignment=TA_CENTER,
        )

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elements.append(Paragraph(
            f"Generated on: {timestamp}",
            footer_style
        ))

        return elements

    def build_document(self) -> list:
        """Build the complete document"""
        elements = []

        # Header
        elements.extend(self._build_header())

        # Section A: Guide to Applications
        elements.extend(self._build_section_a())

        # Section B: Applicant Details (conditional on type)
        applicant_type = self.data.get('applicant_type', 'Individual')
        if applicant_type in ['Individual', 'Joint']:
            elements.extend(self._build_section_b_individual())
        else:
            elements.extend(self._build_section_b_corporate())

        # Section C: Bank Details
        elements.extend(self._build_section_c())

        # Residency Classification
        elements.extend(self._build_residency_section())

        # Investor Category
        elements.extend(self._build_investor_category_section())

        # Section D: Distribution Agents
        elements.extend(self._build_section_d())

        # Witness Section (if applicable)
        elements.extend(self._build_witness_section())

        # Signature Section
        elements.extend(self._build_signature_section())

        # Footer
        elements.extend(self._build_footer())

        return elements

    def generate(self, output_path: str) -> bool:
        """
        Generate the PDF document.

        Args:
            output_path: Path where the PDF will be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=self.margin,
                rightMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin,
            )

            elements = self.build_document()
            doc.build(elements)
            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
