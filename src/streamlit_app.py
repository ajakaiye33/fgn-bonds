"""
FGN Savings Bond Subscription Form - Multi-Step Wizard Application

A Streamlit web application for submitting Federal Government of Nigeria
Savings Bond applications with a multi-step wizard interface.

Author: Hedgar Ajakaiye
License: MIT
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from form_handler import FormHandler
from pymongo import MongoClient
from dotenv import load_dotenv
import pytz
import tempfile
import os
import base64
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set page config first (must be the first Streamlit command)
st.set_page_config(
    page_title="FGN Savings Bond Subscription Form",
    page_icon="💰",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Apply design system theme
from design_system import apply_theme
apply_theme("dark")

# Apply accessibility and responsive features
from accessibility import setup_accessibility
from responsive import setup_responsive
from error_handling import setup_error_handling

setup_accessibility()
setup_responsive()
setup_error_handling()

# Import components
from components import FormWizard
from components.form_fields import (
    validated_text_input,
    validated_email_input,
    validated_phone_input,
    validated_bvn_input,
    currency_input,
    validate_required,
    validate_email,
    validate_phone,
    validate_bvn,
)
from components.feedback import (
    show_loading_spinner,
    show_success_message,
    show_error_message,
    show_info_card,
)

# =============================================================================
# Constants
# =============================================================================

INVESTOR_CATEGORIES = [
    "Individual",
    "Insurance",
    "Corporate",
    "Others",
    "*Foreign Investor",
    "Non-Bank Financial Institution",
    "Co-operative Society",
    "Government Agencies",
    "Staff Scheme",
    "Micro Finance Bank",
]

NIGERIAN_BANKS = [
    "Access Bank",
    "Citibank Nigeria",
    "Ecobank Nigeria",
    "Fidelity Bank",
    "First Bank of Nigeria",
    "First City Monument Bank (FCMB)",
    "Globus Bank",
    "Guaranty Trust Bank (GTBank)",
    "Heritage Bank",
    "Keystone Bank",
    "Polaris Bank",
    "Providus Bank",
    "Stanbic IBTC Bank",
    "Standard Chartered Bank",
    "Sterling Bank",
    "SunTrust Bank",
    "Titan Trust Bank",
    "Union Bank of Nigeria",
    "United Bank for Africa (UBA)",
    "Unity Bank",
    "Wema Bank",
    "Zenith Bank",
    "Other",
]

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# =============================================================================
# Database Initialization
# =============================================================================

@st.cache_resource
def init_mongo():
    """Initialize MongoDB connection with fallback to local storage."""
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[os.getenv('DB_NAME', 'fgn_bonds')]
        return db[os.getenv('COLLECTION_NAME', 'applications')]
    except Exception as e:
        st.warning(f"MongoDB connection failed: {e}. Using local file storage instead.")
        return None


def save_to_mongodb(data: dict) -> tuple:
    """Save application data to MongoDB or local file."""
    try:
        collection = init_mongo()

        if collection is None:
            # Fallback to local file storage
            os.makedirs('data', exist_ok=True)
            import uuid
            submission_id = str(uuid.uuid4())

            if isinstance(data.get('submission_date'), datetime):
                data['submission_date'] = data['submission_date'].strftime('%Y-%m-%d %H:%M:%S')

            data['_id'] = submission_id

            import json
            file_path = os.path.join('data', f"{submission_id}.json")
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True, submission_id
        else:
            if isinstance(data.get('submission_date'), datetime):
                data['submission_date'] = data['submission_date'].strftime('%Y-%m-%d %H:%M:%S')

            result = collection.insert_one(data)
            return True, str(result.inserted_id)
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        return False, error_details


# =============================================================================
# Session State Initialization
# =============================================================================

def initialize_session_state():
    """Initialize all form fields in session state with default values."""
    defaults = {
        # Bond Details
        'tenor': "2-Year",
        'bond_value': 5000.0,
        'amount_words': "",
        'month_of_offer': datetime.now().strftime('%B'),

        # Applicant Type
        'applicant_type': "Individual",

        # Individual/Primary Applicant Details
        'title': "Mr.",
        'full_name': "",
        'date_of_birth': None,
        'phone': "",
        'occupation': "",
        'passport_no': "",
        'next_of_kin': "",
        'address': "",
        'mothers_maiden': "",
        'email': "",
        'cscs_number': "",
        'chn_number': "",

        # Bank Details
        'bank_name': "",
        'bank_branch': "",
        'account_number': "",
        'sort_code': "",
        'bvn': "",

        # Classification
        'is_resident': "Resident",
        'investor_category': [],

        # Distribution Agent
        'agent_name': "",
        'stockbroker_code': "",

        # Witness Section (for illiterate applicants)
        'needs_witness': False,
        'witness_name': "",
        'witness_address': "",
        'witness_acknowledged': False,

        # Joint Applicant defaults
        'joint_title': "Mr.",
        'joint_full_name': "",
        'joint_phone': "",
        'joint_occupation': "",
        'joint_passport_no': "",
        'joint_next_of_kin': "",
        'joint_address': "",
        'joint_email': "",
        'joint_bank_name': "",
        'joint_account_number': "",

        # Corporate defaults
        'company_name': "",
        'rc_number': "",
        'business_type': "",
        'contact_person': "",
        'corp_phone': "",
        'corp_email': "",
        'corp_passport_no': "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# Step Validation Functions
# =============================================================================

def validate_bond_details(data: dict) -> tuple:
    """Validate bond details step."""
    errors = []

    bond_value = data.get('bond_value', 0)
    if bond_value < 5000:
        errors.append("Bond value must be at least ₦5,000.00")
    if bond_value > 50_000_000:
        errors.append("Bond value cannot exceed ₦50,000,000.00")

    if not data.get('tenor'):
        errors.append("Please select a tenor")

    if not data.get('month_of_offer'):
        errors.append("Please select the month of offer")

    return len(errors) == 0, errors


def validate_applicant_type(data: dict) -> tuple:
    """Validate applicant type step."""
    errors = []

    if not data.get('applicant_type'):
        errors.append("Please select an applicant type")

    return len(errors) == 0, errors


def validate_applicant_info(data: dict) -> tuple:
    """Validate applicant information step."""
    errors = []
    applicant_type = data.get('applicant_type', 'Individual')

    if applicant_type in ['Individual', 'Joint']:
        if not data.get('full_name', '').strip():
            errors.append("Full name is required")

        if not data.get('address', '').strip():
            errors.append("Address is required")

        email = data.get('email', '')
        if email:
            result = validate_email(email)
            if not result.is_valid:
                errors.append(result.error_message)

        phone = data.get('phone', '')
        if phone:
            result = validate_phone(phone)
            if not result.is_valid:
                errors.append(result.error_message)

        # Joint applicant validation
        if applicant_type == 'Joint':
            if not data.get('joint_full_name', '').strip():
                errors.append("Joint applicant full name is required")
            if not data.get('joint_address', '').strip():
                errors.append("Joint applicant address is required")

    elif applicant_type == 'Corporate':
        if not data.get('company_name', '').strip():
            errors.append("Company name is required")
        if not data.get('rc_number', '').strip():
            errors.append("RC number is required")
        if not data.get('contact_person', '').strip():
            errors.append("Contact person is required")

    return len(errors) == 0, errors


def validate_bank_details(data: dict) -> tuple:
    """Validate bank details step."""
    errors = []

    if not data.get('bank_name', '').strip():
        errors.append("Bank name is required")

    account = data.get('account_number', '')
    if not account:
        errors.append("Account number is required")
    elif len(account.replace(' ', '')) != 10:
        errors.append("Account number must be 10 digits")

    bvn = data.get('bvn', '')
    if bvn:
        result = validate_bvn(bvn)
        if not result.is_valid:
            errors.append(result.error_message)

    return len(errors) == 0, errors


def validate_classification(data: dict) -> tuple:
    """Validate classification step."""
    errors = []

    if not data.get('is_resident'):
        errors.append("Please select residency status")

    # Investor category is optional but recommended

    return len(errors) == 0, errors


def validate_distribution(data: dict) -> tuple:
    """Validate distribution agent step."""
    # Distribution agent details are optional
    return True, []


# =============================================================================
# Step Renderer Functions
# =============================================================================

def render_bond_details_step():
    """Render Step 1: Bond Details."""
    show_info_card(
        "Bond Information",
        "Select your bond preferences including tenor, value, and month of offer.",
        color="green"
    )

    col1, col2 = st.columns(2)

    with col1:
        # Month of Offer
        current_month = datetime.now().month
        st.session_state.month_of_offer = st.selectbox(
            "Month of Offer",
            MONTHS,
            index=MONTHS.index(st.session_state.get('month_of_offer', MONTHS[current_month - 1])),
            key="month_of_offer_select"
        )

        # Tenor Selection
        st.session_state.tenor = st.radio(
            "Tenor of Bond",
            ["2-Year", "3-Year"],
            index=0 if st.session_state.get('tenor') == "2-Year" else 1,
            horizontal=True,
            key="tenor_select"
        )

        st.info("""
        **Bond Value Limits:**
        - Minimum Value: ₦5,000.00
        - Maximum Value: ₦50,000,000.00
        """)

    with col2:
        # Bond Value with currency formatting
        value, amount_words, is_valid = currency_input(
            label="Value of Bonds Applied for",
            key="bond_value",
            min_value=5000.0,
            max_value=50_000_000.0,
            step=1000.0,
            show_words=True
        )
        st.session_state.amount_words = amount_words


def render_applicant_type_step():
    """Render Step 2: Applicant Type Selection."""
    show_info_card(
        "Applicant Type",
        "Select the type of application you wish to submit.",
        color="green"
    )

    applicant_type = st.radio(
        "Select Applicant Type",
        ["Individual", "Joint", "Corporate"],
        index=["Individual", "Joint", "Corporate"].index(
            st.session_state.get('applicant_type', 'Individual')
        ),
        horizontal=True,
        key="applicant_type_select"
    )
    st.session_state.applicant_type = applicant_type

    # Show description based on selection
    descriptions = {
        "Individual": "Single applicant subscription for personal investment.",
        "Joint": "Two applicants subscribing together (e.g., spouses, business partners).",
        "Corporate": "Company or organization subscription with corporate documentation.",
    }
    st.caption(descriptions.get(applicant_type, ""))


def render_applicant_info_step():
    """Render Step 3: Applicant Information based on type."""
    applicant_type = st.session_state.get('applicant_type', 'Individual')

    if applicant_type == 'Individual':
        render_individual_applicant_form()
    elif applicant_type == 'Joint':
        render_individual_applicant_form()
        st.divider()
        render_joint_applicant_form()
    else:
        render_corporate_applicant_form()


def render_individual_applicant_form():
    """Render individual/primary applicant form fields."""
    st.subheader("Personal Information")

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Title",
            ["Mr.", "Mrs.", "Miss", "Dr.", "Chief", "Prof.", "Alhaji", "Alhaja"],
            key="title"
        )

        validated_text_input(
            "Full Name (as on ID)",
            key="full_name",
            placeholder="Enter your full name",
            required=True
        )

        st.date_input(
            "Date of Birth",
            min_value=datetime(1940, 1, 1),
            max_value=datetime.now(),
            key="date_of_birth"
        )

        validated_phone_input(
            "Phone Number",
            key="phone",
            placeholder="+2348012345678"
        )

        st.text_input(
            "Occupation",
            key="occupation",
            placeholder="Enter your occupation"
        )

        st.text_input(
            "Passport No. (Optional)",
            key="passport_no",
            placeholder="Enter passport number if available"
        )

    with col2:
        validated_email_input(
            "Email Address",
            key="email",
            placeholder="example@email.com"
        )

        st.text_input(
            "Mother's Maiden Name",
            key="mothers_maiden",
            placeholder="Enter mother's maiden name"
        )

        st.text_input(
            "Next of Kin",
            key="next_of_kin",
            placeholder="Enter next of kin name"
        )

        st.text_area(
            "Residential Address",
            key="address",
            placeholder="Enter your full address"
        )

    # E-Allotment Details
    st.subheader("E-Allotment Details")
    col3, col4 = st.columns(2)

    with col3:
        st.text_input(
            "CSCS A/C No.",
            key="cscs_number",
            placeholder="Enter CSCS account number",
            help="Central Securities Clearing System account number"
        )

    with col4:
        st.text_input(
            "CHN No.",
            key="chn_number",
            placeholder="Enter CHN number",
            help="Clearing House Number"
        )


def render_joint_applicant_form():
    """Render joint applicant form fields."""
    st.subheader("Joint Applicant Information")

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Title (Joint)",
            ["Mr.", "Mrs.", "Miss", "Dr.", "Chief", "Prof.", "Alhaji", "Alhaja"],
            key="joint_title"
        )

        validated_text_input(
            "Full Name (Joint)",
            key="joint_full_name",
            placeholder="Enter joint applicant's full name",
            required=True
        )

        validated_phone_input(
            "Phone Number (Joint)",
            key="joint_phone",
            placeholder="+2348012345678"
        )

        st.text_input(
            "Occupation (Joint)",
            key="joint_occupation",
            placeholder="Enter occupation"
        )

    with col2:
        validated_email_input(
            "Email (Joint)",
            key="joint_email",
            placeholder="example@email.com",
            required=False
        )

        st.text_input(
            "Next of Kin (Joint)",
            key="joint_next_of_kin",
            placeholder="Enter next of kin name"
        )

        st.text_area(
            "Address (Joint)",
            key="joint_address",
            placeholder="Enter joint applicant's address"
        )

        st.text_input(
            "Passport No. (Joint, Optional)",
            key="joint_passport_no",
            placeholder="Enter passport number if available"
        )


def render_corporate_applicant_form():
    """Render corporate applicant form fields."""
    st.subheader("Company Information")

    col1, col2 = st.columns(2)

    with col1:
        validated_text_input(
            "Company Name",
            key="company_name",
            placeholder="Enter registered company name",
            required=True
        )

        validated_text_input(
            "RC Number",
            key="rc_number",
            placeholder="Enter company registration number",
            required=True
        )

        st.text_input(
            "Type of Business",
            key="business_type",
            placeholder="Enter type of business"
        )

        st.text_input(
            "Passport No. (Optional)",
            key="corp_passport_no",
            placeholder="Company representative's passport"
        )

    with col2:
        validated_text_input(
            "Contact Person",
            key="contact_person",
            placeholder="Enter authorized contact person",
            required=True
        )

        validated_phone_input(
            "Phone Number",
            key="corp_phone",
            placeholder="+2348012345678"
        )

        validated_email_input(
            "Email Address",
            key="corp_email",
            placeholder="company@email.com"
        )

    # E-Allotment Details for Corporate
    st.subheader("E-Allotment Details")
    col3, col4 = st.columns(2)

    with col3:
        st.text_input(
            "CSCS A/C No.",
            key="cscs_number",
            placeholder="Enter CSCS account number"
        )

    with col4:
        st.text_input(
            "CHN No.",
            key="chn_number",
            placeholder="Enter CHN number"
        )


def render_bank_details_step():
    """Render Step 4: Bank Details."""
    show_info_card(
        "Bank Information",
        "Enter your bank details for interest payment and redemption proceeds.",
        color="green"
    )

    col1, col2 = st.columns(2)

    with col1:
        # Bank selection
        bank_name = st.selectbox(
            "Bank Name",
            NIGERIAN_BANKS,
            key="bank_name_select"
        )

        if bank_name == "Other":
            st.session_state.bank_name = st.text_input(
                "Specify Bank Name",
                key="bank_name_other"
            )
        else:
            st.session_state.bank_name = bank_name

        st.text_input(
            "Bank Branch",
            key="bank_branch",
            placeholder="Enter bank branch"
        )

        st.text_input(
            "Sort Code",
            key="sort_code",
            placeholder="Enter bank sort code"
        )

    with col2:
        validated_text_input(
            "Account Number",
            key="account_number",
            placeholder="Enter 10-digit account number",
            required=True
        )

        validated_bvn_input(
            "BVN",
            key="bvn",
            help_text="Your 11-digit Bank Verification Number"
        )


def render_classification_step():
    """Render Step 5: Classification (Residency and Investor Category)."""
    show_info_card(
        "Classification",
        "Indicate your residency status and investor category.",
        color="green"
    )

    # Residency Status
    st.subheader("Residency Status")
    st.session_state.is_resident = st.radio(
        "Select Residency Status",
        ["Resident", "Non-Resident"],
        index=0 if st.session_state.get('is_resident') == "Resident" else 1,
        horizontal=True,
        key="residency_select"
    )

    st.caption(
        "**Resident:** Nigerian citizens residing in Nigeria or foreigners living in Nigeria. "
        "**Non-Resident:** Nigerian citizens or foreigners residing outside Nigeria."
    )

    st.divider()

    # Investor Category (Multi-select checkboxes)
    st.subheader("Investor Category")
    st.caption("Select all categories that apply to you:")

    # Create checkbox grid for investor categories
    selected_categories = []
    cols = st.columns(2)

    for i, category in enumerate(INVESTOR_CATEGORIES):
        with cols[i % 2]:
            if st.checkbox(
                category,
                key=f"investor_cat_{i}",
                value=category in st.session_state.get('investor_category', [])
            ):
                selected_categories.append(category)

    st.session_state.investor_category = selected_categories


def render_distribution_step():
    """Render Step 6: Distribution Agent and Witness Section."""
    show_info_card(
        "Distribution Agent",
        "Enter the details of your distribution agent or stockbroker.",
        color="green"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Distribution Agent / Receiving Agent",
            key="agent_name",
            placeholder="Enter agent name"
        )

    with col2:
        st.text_input(
            "Stockbroker Code",
            key="stockbroker_code",
            placeholder="Enter stockbroker code"
        )

    st.divider()

    # Witness Section (for illiterate applicants)
    st.subheader("Witness Section")
    st.caption("Complete this section only if the applicant cannot sign (thumbprint will be used)")

    needs_witness = st.checkbox(
        "Applicant cannot sign (requires witness)",
        key="needs_witness"
    )

    if needs_witness:
        col3, col4 = st.columns(2)

        with col3:
            st.text_input(
                "Witness Name",
                key="witness_name",
                placeholder="Enter witness full name"
            )

        with col4:
            st.text_area(
                "Witness Address",
                key="witness_address",
                placeholder="Enter witness address"
            )

        st.checkbox(
            "I confirm that I have witnessed this application and the thumbprint belongs to the applicant",
            key="witness_acknowledged"
        )


def render_review_step():
    """Render Step 7: Review and Submit."""
    show_info_card(
        "Review Your Application",
        "Please review all information before submitting. Click on any section to expand.",
        color="green"
    )

    # Bond Details Summary
    with st.expander("Bond Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Tenor:** {st.session_state.get('tenor', 'N/A')}")
            st.write(f"**Month of Offer:** {st.session_state.get('month_of_offer', 'N/A')}")
        with col2:
            st.write(f"**Bond Value:** ₦{st.session_state.get('bond_value', 0):,.2f}")
            st.write(f"**Amount in Words:** {st.session_state.get('amount_words', 'N/A')}")

    # Applicant Information Summary
    applicant_type = st.session_state.get('applicant_type', 'Individual')
    with st.expander(f"Applicant Information ({applicant_type})", expanded=True):
        if applicant_type in ['Individual', 'Joint']:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {st.session_state.get('title', 'N/A')}")
                st.write(f"**Full Name:** {st.session_state.get('full_name', 'N/A')}")
                st.write(f"**Phone:** {st.session_state.get('phone', 'N/A')}")
                st.write(f"**Occupation:** {st.session_state.get('occupation', 'N/A')}")
            with col2:
                st.write(f"**Email:** {st.session_state.get('email', 'N/A')}")
                st.write(f"**Address:** {st.session_state.get('address', 'N/A')}")
                dob = st.session_state.get('date_of_birth')
                st.write(f"**Date of Birth:** {dob.strftime('%Y-%m-%d') if dob else 'N/A'}")

            if applicant_type == 'Joint':
                st.divider()
                st.write("**Joint Applicant:**")
                st.write(f"- Name: {st.session_state.get('joint_full_name', 'N/A')}")
                st.write(f"- Phone: {st.session_state.get('joint_phone', 'N/A')}")
                st.write(f"- Email: {st.session_state.get('joint_email', 'N/A')}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company Name:** {st.session_state.get('company_name', 'N/A')}")
                st.write(f"**RC Number:** {st.session_state.get('rc_number', 'N/A')}")
            with col2:
                st.write(f"**Contact Person:** {st.session_state.get('contact_person', 'N/A')}")
                st.write(f"**Phone:** {st.session_state.get('corp_phone', 'N/A')}")

    # Bank Details Summary
    with st.expander("Bank Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Bank Name:** {st.session_state.get('bank_name', 'N/A')}")
            st.write(f"**Account Number:** {st.session_state.get('account_number', 'N/A')}")
        with col2:
            st.write(f"**BVN:** {st.session_state.get('bvn', 'N/A')}")
            st.write(f"**CSCS A/C No:** {st.session_state.get('cscs_number', 'N/A')}")

    # Classification Summary
    with st.expander("Classification", expanded=True):
        st.write(f"**Residency Status:** {st.session_state.get('is_resident', 'N/A')}")
        categories = st.session_state.get('investor_category', [])
        st.write(f"**Investor Categories:** {', '.join(categories) if categories else 'None selected'}")

    # Distribution Agent Summary
    with st.expander("Distribution Agent", expanded=True):
        st.write(f"**Agent Name:** {st.session_state.get('agent_name', 'N/A')}")
        st.write(f"**Stockbroker Code:** {st.session_state.get('stockbroker_code', 'N/A')}")

    # Terms and confirmation
    st.divider()
    st.warning("""
    **Declaration:**
    By submitting this application, I/we hereby confirm that:
    - All information provided is true and accurate
    - I/we have read and understood the terms and conditions of the FGN Savings Bond
    - I/we authorize the debit of my/our bank account for the subscription amount
    """)


# =============================================================================
# Form Data Collection
# =============================================================================

def collect_form_data() -> dict:
    """Collect all form data from session state."""
    nigeria_tz = pytz.timezone("Africa/Lagos")
    current_time = datetime.now(nigeria_tz)

    data = {
        'submission_date': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'submission_timezone': 'Africa/Lagos',

        # Bond Details
        'tenor': st.session_state.get('tenor', ''),
        'month_of_offer': st.session_state.get('month_of_offer', ''),
        'bond_value': float(st.session_state.get('bond_value', 0)),
        'amount_in_words': st.session_state.get('amount_words', ''),

        # Applicant Type
        'applicant_type': st.session_state.get('applicant_type', ''),

        # Individual/Primary Applicant Details
        'title': st.session_state.get('title', ''),
        'full_name': st.session_state.get('full_name', ''),
        'date_of_birth': st.session_state.get('date_of_birth', ''),
        'phone_number': st.session_state.get('phone', ''),
        'occupation': st.session_state.get('occupation', ''),
        'passport_no': st.session_state.get('passport_no', ''),
        'next_of_kin': st.session_state.get('next_of_kin', ''),
        'address': st.session_state.get('address', ''),
        'mothers_maiden_name': st.session_state.get('mothers_maiden', ''),
        'email': st.session_state.get('email', ''),
        'cscs_number': st.session_state.get('cscs_number', ''),
        'chn_number': st.session_state.get('chn_number', ''),

        # Bank Details
        'bank_name': st.session_state.get('bank_name', ''),
        'bank_branch': st.session_state.get('bank_branch', ''),
        'account_number': st.session_state.get('account_number', ''),
        'sort_code': st.session_state.get('sort_code', ''),
        'bvn': st.session_state.get('bvn', ''),

        # Classification
        'is_resident': st.session_state.get('is_resident', 'Resident') == "Resident",
        'investor_category': st.session_state.get('investor_category', []),

        # Distribution Agent
        'agent_name': st.session_state.get('agent_name', ''),
        'stockbroker_code': st.session_state.get('stockbroker_code', ''),

        # Witness Section
        'needs_witness': st.session_state.get('needs_witness', False),
        'witness_name': st.session_state.get('witness_name', ''),
        'witness_address': st.session_state.get('witness_address', ''),
        'witness_acknowledged': st.session_state.get('witness_acknowledged', False),

        # Joint Applicant Details
        'joint_title': st.session_state.get('joint_title', ''),
        'joint_full_name': st.session_state.get('joint_full_name', ''),
        'joint_phone_number': st.session_state.get('joint_phone', ''),
        'joint_occupation': st.session_state.get('joint_occupation', ''),
        'joint_passport_no': st.session_state.get('joint_passport_no', ''),
        'joint_next_of_kin': st.session_state.get('joint_next_of_kin', ''),
        'joint_address': st.session_state.get('joint_address', ''),
        'joint_email': st.session_state.get('joint_email', ''),
        'joint_bank_name': st.session_state.get('joint_bank_name', ''),
        'joint_account_number': st.session_state.get('joint_account_number', ''),

        # Corporate Details
        'company_name': st.session_state.get('company_name', ''),
        'rc_number': st.session_state.get('rc_number', ''),
        'business_type': st.session_state.get('business_type', ''),
        'contact_person': st.session_state.get('contact_person', ''),
        'corp_phone_number': st.session_state.get('corp_phone', ''),
        'corp_email': st.session_state.get('corp_email', ''),
        'corp_passport_no': st.session_state.get('corp_passport_no', ''),
    }

    # Convert date to string if present
    if data['date_of_birth'] and hasattr(data['date_of_birth'], 'strftime'):
        data['date_of_birth'] = data['date_of_birth'].strftime('%Y-%m-%d')

    return data


# =============================================================================
# Form Submission Handler
# =============================================================================

def handle_form_submission():
    """Handle final form submission."""
    form_handler = FormHandler()

    # Collect form data
    data = collect_form_data()

    # Validate complete application
    is_valid, errors = form_handler.validate_application(data)

    if not is_valid:
        show_error_message(
            "Please fix the following errors before submitting:",
            title="Validation Error",
            errors=errors
        )
        return

    # Use st.status for progressive feedback during submission
    with st.status("Submitting application...", expanded=True) as status:
        st.write("Validating form data...")

        st.write("Saving to database...")
        # Save to database
        success, result = save_to_mongodb(data)

        if not success:
            status.update(label="Submission failed", state="error")
            show_error_message(
                f"Failed to save application: {result}",
                title="Database Error"
            )
            return

        st.write("Generating PDF document...")
        # Generate PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            form_handler.generate_pdf(data, tmp.name)
            st.session_state['pdf_path'] = tmp.name

        st.write("Finalizing submission...")
        status.update(label="Application submitted successfully!", state="complete", expanded=False)

    # Show success message
    show_success_message(
        f"Your application has been submitted successfully. Reference ID: {result}",
        title="Application Submitted"
    )

    # Show download button
    if 'pdf_path' in st.session_state:
        with open(st.session_state['pdf_path'], 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
            st.download_button(
                label="Download Application PDF",
                data=pdf_bytes,
                file_name="bond_subscription.pdf",
                mime="application/pdf",
                type="primary"
            )

        # Show PDF preview
        st.subheader("PDF Preview")
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Page title
    st.title("FGN Savings Bond Subscription Form")
    st.caption("Federal Government of Nigeria Savings Bond - Digital Application")

    # Initialize session state
    initialize_session_state()

    # Initialize wizard
    wizard = FormWizard()

    # Set up step validation functions
    wizard.STEPS[0].validation_fn = validate_bond_details
    wizard.STEPS[1].validation_fn = validate_applicant_type
    wizard.STEPS[2].validation_fn = validate_applicant_info
    wizard.STEPS[3].validation_fn = validate_bank_details
    wizard.STEPS[4].validation_fn = validate_classification
    wizard.STEPS[5].validation_fn = validate_distribution

    # Define step renderers
    step_renderers = {
        "bond_details": render_bond_details_step,
        "applicant_type": render_applicant_type_step,
        "applicant_info": render_applicant_info_step,
        "bank_details": render_bank_details_step,
        "classification": render_classification_step,
        "distribution": render_distribution_step,
        "review": render_review_step,
    }

    # Render the wizard
    wizard.render(step_renderers, on_submit=handle_form_submission)

    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.subheader("Help & Support")
    st.sidebar.info("""
    **Need Help?**
    - Minimum investment: ₦5,000
    - Maximum investment: ₦50,000,000
    - Available tenors: 2 Years, 3 Years
    - Interest paid quarterly
    """)



if __name__ == "__main__":
    main()
