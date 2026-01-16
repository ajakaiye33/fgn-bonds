from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys
from num2words import num2words
from utils import format_money_in_words
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import pandas as pd
import tempfile
import webbrowser
import logging
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pytz

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

@dataclass
class FGNSBForm:
    # Basic Application Details
    tenor_of_bond: str  # 2-Year or 3-Year
    month_of_offer: str
    year_of_offer: int
    value_of_bonds: float
    amount_in_words: str

    # Individual Applicant Details
    full_name: str
    state_title: str  # Mr., Mrs., Miss
    occupation: str
    phone_no: str
    next_of_kin: str
    address: str
    passport_no: str
    date_of_birth: datetime
    mothers_maiden_name: str
    email: str
    bank_name: str
    bank_account_no: str
    bvn: str
    is_resident: bool

    # CSCS Details
    cscs_account_no: str
    chn_no: str

    # Optional Joint Applicant Details
    joint_full_name: Optional[str] = None
    joint_state_title: Optional[str] = None
    joint_occupation: Optional[str] = None
    joint_phone_no: Optional[str] = None
    joint_next_of_kin: Optional[str] = None
    joint_address: Optional[str] = None
    joint_email: Optional[str] = None
    joint_bank_name: Optional[str] = None
    joint_bank_account_no: Optional[str] = None
    joint_bvn: Optional[str] = None
    joint_is_resident: Optional[bool] = None

    def validate(self) -> tuple[bool, str]:
        """Validate form data"""
        if not self.value_of_bonds >= 5000:
            return False, "Minimum value must be ₦5,000"
        if not self.value_of_bonds <= 50_000_000:
            return False, "Maximum value must be ₦50,000,000"
        # Add more validation rules as needed
        return True, "Valid"

class FormHandler:
    def __init__(self):
        self.assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.setup_logging()
        self.setup_database()

    def setup_logging(self):
        logging.basicConfig(
            filename='bond_application.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_database(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(os.getenv('MONGO_URI'))
            self.db = self.client[os.getenv('DB_NAME')]
            self.collection = self.db[os.getenv('COLLECTION_NAME')]
            logging.info("MongoDB connection established successfully")
        except Exception as e:
            logging.exception(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def save_application(self, data):
        """Save application data to MongoDB"""
        try:
            # Convert datetime objects to strings
            if isinstance(data.get('submission_date'), datetime):
                data['submission_date'] = data['submission_date'].strftime('%Y-%m-%d %H:%M:%S')

            # Insert data into MongoDB
            result = self.collection.insert_one(data)

            logging.info(f"Application saved successfully with ID: {result.inserted_id}")
            return True, str(result.inserted_id)
        except Exception as e:
            logging.exception(f"Failed to save application: {str(e)}")
            return False, str(e)

    def generate_pdf(self, data, output_path):
        """
        Generate PDF form using the new DMO-styled template.

        Args:
            data: Application data dictionary
            output_path: Path to save the PDF

        Returns:
            True if successful
        """
        try:
            from pdf import PDFGenerator
            generator = PDFGenerator()
            generator.generate_subscription_form(data, output_path)
            logging.info(f"PDF generated successfully: {output_path}")
            return True
        except Exception as e:
            logging.exception(f"Failed to generate PDF with new template: {e}")
            # Fallback to legacy PDF generation
            return self._generate_pdf_legacy(data, output_path)

    def _generate_pdf_legacy(self, data, output_path):
        """Legacy PDF generation (fallback)"""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Start with proper spacing from top
        current_height = height - 80

        # Add DMO logo
        logo_path = os.path.join(os.path.dirname(__file__), '../assets/dmo_logo.png')
        if os.path.exists(logo_path):
            c.drawImage(logo_path, width/2 - 50, height - 90, width=100, height=70)

        # Add title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(width/2 - 140, height - 130, "FEDERAL GOVERNMENT OF NIGERIA")
        c.drawString(width/2 - 100, height - 150, "SAVINGS BOND (FGNSB)")
        c.drawString(width/2 - 110, height - 170, "SUBSCRIPTION FORM")

        current_height = height - 200
        section_spacing = 30

        # Draw sections
        current_height = self._draw_guide_section(c, data, width, current_height)
        current_height -= section_spacing/2  # Reduce space after guide section

        if data['applicant_type'] == "Corporate":
            current_height = self._draw_corporate_section(c, data, width, current_height)
        else:
            current_height = self._draw_applicant_section(c, data, width, current_height)
            if data['applicant_type'] == "Joint":
                current_height = self._draw_joint_applicant_section(c, data, width, current_height)

        current_height -= section_spacing/2  # Reduce space before bank details

        current_height = self._draw_bank_details(c, data, width, current_height)
        current_height -= section_spacing/2  # Reduce space before residency

        current_height = self._draw_residency_section(c, data, width, current_height)
        current_height -= section_spacing/2  # Reduce space before distribution

        self._draw_distribution_section(c, data, width, current_height)

        c.save()
        return True

    def _draw_guide_section(self, c, data, width, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y + 20, "A. Guide to Applications")
        y -= 30

        # Use "N" instead of "₦" for Naira symbol to avoid encoding issues
        naira_symbol = "N"

        guide_data = [
            ["Month of Offer:", data['month_of_offer']],
            ["Tenor of Bond:", f"2-Year {'[√]' if data['tenor'] == '2-Year' else '[  ]'}",
             f"3-Year {'[√]' if data['tenor'] == '3-Year' else '[  ]'}"],
            ["Minimum Value:", f"{naira_symbol}5,000.00", ""],
            ["Maximum Value:", f"{naira_symbol}50,000,000.00", ""],
            ["Value of Bonds Applied for:", f"{naira_symbol}{data['bond_value']:,.2f}", ""],
            ["Amount in Words:", data['amount_in_words'], ""]
        ]

        table = Table(guide_data, colWidths=[150, 200, 170])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        table.wrapOn(c, width - 100, y)
        table.drawOn(c, 50, y - 60)
        return y - 100

    def _draw_applicant_section(self, c, data, width, y):
        # Draw section title
        c.setFont("Helvetica-Bold", 12)
        if data['applicant_type'] == "Individual":
            c.drawString(50, y + 30, "B. Individual Applicant Details")
        elif data['applicant_type'] == "Joint":
            c.drawString(50, y + 30, "B. Joint Applicant Details")
        else:
            c.drawString(50, y + 30, "B. Corporate Applicant Details")
        y -= 50

        if data['applicant_type'] == "Individual" or data['applicant_type'] == "Joint":
            applicant_data = [
                ["Title:", data['title']],
                ["Full Name:", data['full_name']],
                ["Date of Birth:", data['date_of_birth']],
                ["Phone Number:", data['phone_number']],
                ["Next of Kin:", data['next_of_kin']],
                ["Address:", data['address']],
                ["Mother's Maiden Name:", data['mothers_maiden_name']],
                ["Email:", data['email']],
                ["CSCS Number:", data['cscs_number']],
                ["CHN Number:", data['chn_number']]
            ]
        else:
            applicant_data = [
                ["Company Name:", data['company_name']],
                ["RC Number:", data['rc_number']],
                ["Business Type:", data['business_type']],
                ["Contact Person:", data['contact_person']],
                ["Phone Number:", data.get('corp_phone_number', data.get('corp_phone', ''))],
                ["Email:", data.get('corp_email', '')]
            ]

        table = Table(applicant_data, colWidths=[150, 370])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.white),
        ]))

        table.wrapOn(c, width - 100, y)
        table.drawOn(c, 50, y - 100)
        y = y - 150

        # Draw joint applicant section if applicable
        if data['applicant_type'] == "Joint" and data['joint_full_name']:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y + 20, "C. Joint Applicant Details")
            y -= 40

            joint_data = [
                ["Title:", data['joint_title']],
                ["Full Name:", data['joint_full_name']],
                ["Phone Number:", data.get('joint_phone_number', data.get('joint_phone', ''))],
                ["Next of Kin:", data['joint_next_of_kin']],
                ["Address:", data['joint_address']],
                ["Email:", data['joint_email']],
                ["Bank Name:", data['joint_bank_name']],
                ["Account Number:", data['joint_account_number']]
            ]

            joint_table = Table(joint_data, colWidths=[150, 370])
            joint_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (0, -1), colors.white),
            ]))

            joint_table.wrapOn(c, width - 100, y)
            joint_table.drawOn(c, 50, y - 100)
            y = y - 150

        return y

    def _draw_joint_applicant_section(self, c, data, width, y):
        if not data.get('joint_full_name'):
            return y - 10

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y + 15, "2. Joint Applicant Details")

        joint_data = [
            ["Title:", data['joint_title']],
            ["Full Name:", data['joint_full_name']],
            ["Phone Number:", data.get('joint_phone_number', data.get('joint_phone', ''))],
            ["Next of Kin:", data['joint_next_of_kin']],
            ["Address:", data['joint_address']],
            ["Email:", data['joint_email']],
            ["Bank Name:", data['joint_bank_name']],
            ["Account Number:", data['joint_account_number']]
        ]

        table = Table(joint_data, colWidths=[150, 370])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        table.wrapOn(c, width, y)
        table.drawOn(c, 50, y - 130)

        return y - 150

    def _draw_corporate_section(self, c, data, width, y):
        if not data.get('company_name'):
            return y - 10

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y + 20, "B. Corporate Applicant Details")
        y -= 30

        corporate_data = [
            ["Company Name:", data['company_name']],
            ["RC Number:", data['rc_number']],
            ["Business Type:", data['business_type']],
            ["Contact Person:", data['contact_person']],
            ["Phone Number:", data.get('corp_phone_number', data.get('corp_phone', ''))],
            ["Email:", data.get('corp_email', '')]
        ]

        table = Table(corporate_data, colWidths=[150, 370])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.white),
        ]))

        table.wrapOn(c, width, y)
        table.drawOn(c, 50, y - 60)

        return y - 100

    def _draw_bank_details(self, c, data, width, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y + 20, "C. Bank Details")
        y -= 30

        bank_data = [
            ["Bank Name:", data['bank_name']],
            ["Bank Branch:", data['bank_branch']],
            ["Account Number:", data['account_number']],
            ["Sort Code:", data['sort_code']],
            ["BVN:", data['bvn']]
        ]

        table = Table(bank_data, colWidths=[150, 370])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.white),
        ]))

        table.wrapOn(c, width - 100, y)
        table.drawOn(c, 50, y - 60)
        return y - 100

    def _draw_residency_section(self, c, data, width, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y + 20, "D. Residency Classification")

        # Draw checkboxes
        c.rect(50, y - 30, 15, 15)
        c.rect(150, y - 30, 15, 15)

        if data['is_resident']:
            c.drawString(53, y - 27, "√")
        else:
            c.drawString(153, y - 27, "√")

        c.setFont("Helvetica", 10)
        c.drawString(70, y - 27, "Resident")
        c.drawString(170, y - 27, "Non-Resident")

        return y - 40

    def _draw_distribution_section(self, c, data, width, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y + 15, "E. Distribution Agents")

        dist_data = [
            ["Distribution Agent:", data['agent_name']],
            ["Stockbroker Code:", data['stockbroker_code']]
        ]

        table = Table(dist_data, colWidths=[150, 370])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        table.wrapOn(c, width, y)
        table.drawOn(c, 50, y - 25)

        # Calculate new y position after table
        y = y - 60

        # Add signature section header with proper spacing
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Signature Section")

        # Create a table for the signature section for better alignment
        signature_data = [
            ["Generated on: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Page 1 of 1"]
        ]

        # Create a table for the signature boxes
        sig_table = Table([["", ""]], colWidths=[width/2 - 60, width/2 - 60])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
            ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
            ('HEIGHT', (0, 0), (-1, -1), 50),
        ]))

        # Position the signature table
        y -= 20
        sig_table.wrapOn(c, width - 100, 50)
        sig_table.drawOn(c, 50, y - 50)

        # Add signature labels
        c.setFont("Helvetica", 10)
        c.drawString(100, y - 65, "Applicant's Signature")
        c.drawString(width/2 + 50, y - 65, "Date (DD/MM/YYYY)")

        # Create footer table for better alignment
        footer_table = Table(signature_data, colWidths=[width/2 - 60, width/2 - 60])
        footer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))

        # Position the footer
        footer_table.wrapOn(c, width - 100, 20)
        footer_table.drawOn(c, 50, 30)

        return y

    def collect_form_data(self, gui_data):
        """Prepare data for PDF generation with additional formatting"""
        data = gui_data.copy()
        data['amount_in_words'] = format_money_in_words(float(data['bond_value']))
        return data

    def export_to_csv(self, file_path: str) -> bool:
        """Export all applications to CSV"""
        try:
            # Get all applications from MongoDB
            applications = list(self.collection.find({}))

            # Convert to DataFrame
            df = pd.DataFrame(applications)

            # Convert ObjectId to string for CSV export
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)

            # Export to CSV
            df.to_csv(file_path, index=False)
            logging.info(f"Data exported to CSV: {file_path}")
            return True
        except Exception as e:
            logging.exception(f"Failed to export CSV: {str(e)}")
            return False

    def export_to_excel(self, file_path: str) -> bool:
        """Export all applications to Excel"""
        try:
            # Get all applications from MongoDB
            applications = list(self.collection.find({}))

            # Convert to DataFrame
            df = pd.DataFrame(applications)

            # Convert ObjectId to string for Excel export
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)

            # Export to Excel
            df.to_excel(file_path, index=False)
            logging.info(f"Data exported to Excel: {file_path}")
            return True
        except Exception as e:
            logging.exception(f"Failed to export Excel: {str(e)}")
            return False

    def preview_pdf(self, data: Dict) -> bool:
        """Generate and preview PDF in default browser"""
        try:
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                self.generate_pdf(data, tmp.name)
                webbrowser.open(f'file://{tmp.name}')
            logging.info("PDF preview generated successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to preview PDF: {str(e)}")
            return False

    def save_form_data(self, data: Dict, file_path: str) -> bool:
        """Save form data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            logging.info(f"Form data saved to: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to save form data: {str(e)}")
            return False

    def load_form_data(self, file_path: str) -> Optional[Dict]:
        """Load form data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            logging.info(f"Form data loaded from: {file_path}")
            return data
        except Exception as e:
            logging.error(f"Failed to load form data: {str(e)}")
            return None

    def get_monthly_report(self, year: int, month: int) -> pd.DataFrame:
        """Generate monthly subscription report

        Args:
            year: The year to filter by
            month: The month to filter by (1-12)

        Returns:
            DataFrame containing the monthly report data
        """
        try:
            # Convert month to string name for matching
            month_name = datetime(year, month, 1).strftime('%B')

            # Query MongoDB for applications in the specified month and year
            query = {
                "month_of_offer": month_name,
                "submission_date": {"$regex": f"^{year}-{month:02d}"}
            }

            applications = list(self.collection.find(query))

            if not applications:
                logging.info(f"No applications found for {month_name} {year}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(applications)

            # Convert ObjectId to string
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)

            # Add calculated columns
            if 'bond_value' in df.columns:
                df['bond_value'] = df['bond_value'].astype(float)

            logging.info(f"Generated monthly report for {month_name} {year} with {len(df)} applications")
            return df

        except Exception as e:
            logging.exception(f"Failed to generate monthly report: {str(e)}")
            return pd.DataFrame()

    def get_subscription_summary(self) -> Dict:
        """Generate summary statistics for all subscriptions

        Returns:
            Dictionary containing summary statistics
        """
        try:
            # Get all applications
            applications = list(self.collection.find({}))

            if not applications:
                return {
                    "total_applications": 0,
                    "total_value": 0,
                    "average_value": 0,
                    "applicant_types": {},
                    "months": {},
                    "value_distribution": {},
                    "daily_trend": {},
                    "top_applicants": []
                }

            # Convert to DataFrame
            df = pd.DataFrame(applications)

            # Calculate summary statistics
            total_applications = len(df)
            total_value = df['bond_value'].astype(float).sum()
            average_value = total_value / total_applications if total_applications > 0 else 0

            # Count by applicant type
            applicant_types = df['applicant_type'].value_counts().to_dict() if 'applicant_type' in df.columns else {}

            # Count by month
            if 'month_of_offer' in df.columns:
                months = df['month_of_offer'].value_counts().to_dict()
            else:
                months = {}

            # Value distribution (group bond values into ranges)
            value_distribution = {}
            if 'bond_value' in df.columns:
                # Define ranges
                ranges = [
                    (0, 10000, "₦0 - ₦10,000"),
                    (10000, 50000, "₦10,000 - ₦50,000"),
                    (50000, 100000, "₦50,000 - ₦100,000"),
                    (100000, 500000, "₦100,000 - ₦500,000"),
                    (500000, 1000000, "₦500,000 - ₦1,000,000"),
                    (1000000, float('inf'), "₦1,000,000+")
                ]

                for start, end, label in ranges:
                    count = len(df[(df['bond_value'] >= start) & (df['bond_value'] < end)])
                    value_distribution[label] = count

            # Daily trend analysis
            daily_trend = {}
            if 'submission_date' in df.columns:
                # Extract date part only
                df['submission_day'] = df['submission_date'].apply(
                    lambda x: x.split(' ')[0] if isinstance(x, str) else str(x)[:10]
                )
                daily_counts = df['submission_day'].value_counts().to_dict()

                # Sort by date
                daily_trend = {k: daily_counts[k] for k in sorted(daily_counts.keys())}

            # Top applicants by bond value
            top_applicants = []
            if 'bond_value' in df.columns:
                # Create name column based on applicant type
                if 'applicant_type' in df.columns:
                    df['applicant_name'] = df.apply(
                        lambda x: x.get('company_name', '') if x.get('applicant_type') == 'Corporate'
                        else x.get('full_name', ''),
                        axis=1
                    )

                    # Get top 5 applicants by bond value
                    top_df = df.sort_values('bond_value', ascending=False).head(5)
                    top_applicants = [
                        {
                            'name': row.get('applicant_name', 'Unknown'),
                            'type': row.get('applicant_type', 'Unknown'),
                            'value': float(row.get('bond_value', 0)),
                            'date': row.get('submission_date', 'Unknown')
                        }
                        for _, row in top_df.iterrows()
                    ]

            # Calculate week-over-week growth
            wow_growth = 0
            if 'submission_date' in df.columns:
                try:
                    # Convert to datetime
                    df['submission_datetime'] = pd.to_datetime(df['submission_date'])

                    # Get current date and calculate dates for analysis
                    current_date = datetime.now()
                    one_week_ago = current_date - pd.Timedelta(days=7)
                    two_weeks_ago = current_date - pd.Timedelta(days=14)

                    # Count applications in each period
                    current_week_count = len(df[df['submission_datetime'] >= one_week_ago])
                    previous_week_count = len(df[(df['submission_datetime'] >= two_weeks_ago) &
                                                (df['submission_datetime'] < one_week_ago)])

                    # Calculate growth percentage
                    if previous_week_count > 0:
                        wow_growth = ((current_week_count - previous_week_count) / previous_week_count) * 100
                except Exception as e:
                    logging.warning(f"Could not calculate week-over-week growth: {str(e)}")

            return {
                "total_applications": total_applications,
                "total_value": total_value,
                "average_value": average_value,
                "applicant_types": applicant_types,
                "months": months,
                "value_distribution": value_distribution,
                "daily_trend": daily_trend,
                "top_applicants": top_applicants,
                "wow_growth": wow_growth
            }

        except Exception as e:
            logging.exception(f"Failed to generate subscription summary: {str(e)}")
            return {
                "total_applications": 0,
                "total_value": 0,
                "average_value": 0,
                "applicant_types": {},
                "months": {},
                "value_distribution": {},
                "daily_trend": {},
                "top_applicants": [],
                "wow_growth": 0
            }

    def validate_application(self, data: Dict) -> Tuple[bool, List[str]]:
        """Comprehensive validation of application data"""
        errors = []

        # Validate bond value
        try:
            bond_value = float(data.get('bond_value', 0))
            if not 5000 <= bond_value <= 50_000_000:
                errors.append("Bond value must be between ₦5,000 and ₦50,000,000")
        except ValueError:
            errors.append("Invalid bond value")

        # Validate required fields based on applicant type
        if data.get('applicant_type') == "Corporate":
            required_fields = {
                'company_name': "Company Name",
                'rc_number': "RC Number",
                'business_type': "Business Type",
                'contact_person': "Contact Person",
                'corp_phone_number': "Phone Number",
                'corp_email': "Email",
                'bank_name': "Bank Name",
                'account_number': "Account Number",
                'bvn': "BVN"
            }
        else:
            # Individual or Joint applicant
            required_fields = {
                'full_name': "Full Name",
                'phone_number': "Phone Number",
                'email': "Email",
                'cscs_number': "CSCS Number",
                'bank_name': "Bank Name",
                'account_number': "Account Number",
                'bvn': "BVN"
            }

            # Additional validation for joint applicant
            if data.get('applicant_type') == "Joint":
                joint_required = {
                    'joint_full_name': "Joint Applicant Full Name",
                    'joint_phone_number': "Joint Applicant Phone Number",
                    'joint_email': "Joint Applicant Email"
                }
                required_fields.update(joint_required)

        for field, label in required_fields.items():
            if not data.get(field):
                errors.append(f"{label} is required")

        # Validate email format
        if data.get('applicant_type') == "Corporate":
            if data.get('corp_email') and '@' not in data['corp_email']:
                errors.append("Invalid corporate email format")
        else:
            if data.get('email') and '@' not in data['email']:
                errors.append("Invalid email format")
            if data.get('applicant_type') == "Joint":
                if data.get('joint_email') and '@' not in data['joint_email']:
                    errors.append("Invalid joint applicant email format")

        # Validate phone number
        if data.get('applicant_type') == "Corporate":
            if data.get('corp_phone_number') and not data['corp_phone_number'].replace('+', '').isdigit():
                errors.append("Corporate phone number must contain only digits")
        else:
            if data.get('phone_number') and not data['phone_number'].replace('+', '').isdigit():
                errors.append("Phone number must contain only digits")
            if data.get('applicant_type') == "Joint":
                if data.get('joint_phone_number') and not data['joint_phone_number'].replace('+', '').isdigit():
                    errors.append("Joint applicant phone number must contain only digits")

        # Validate BVN
        if data.get('bvn') and len(data['bvn']) != 11:
            errors.append("BVN must be 11 digits")

        logging.info(f"Validation completed with {len(errors)} errors")
        return len(errors) == 0, errors