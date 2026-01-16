"""
FGN Savings Bond Admin Dashboard

Enhanced admin interface with advanced filtering, pagination, and export capabilities.

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
import os
import base64
import tempfile
import hashlib
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set page config first (must be the first Streamlit command)
st.set_page_config(
    page_title="FGN Savings Bond Admin Dashboard",
    page_icon="🔐",
    layout="wide"
)

# Apply design system dark theme for admin (easier on the eyes)
from design_system import apply_theme
apply_theme("dark")

# Apply accessibility and responsive features
from accessibility import setup_accessibility
from responsive import setup_responsive
from error_handling import setup_error_handling

setup_accessibility()
setup_responsive()
setup_error_handling()

# Import admin modules
from admin import (
    FilterPanel,
    render_filter_panel,
    apply_filters,
    PaginatedTable,
    render_paginated_table,
    ExportManager,
)


# =============================================================================
# Database Initialization
# =============================================================================

@st.cache_resource
def init_mongo():
    """Initialize MongoDB connection."""
    try:
        client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[os.getenv('DB_NAME', 'fgn_bonds')]
        return db[os.getenv('COLLECTION_NAME', 'applications')]
    except Exception as e:
        st.error(f"MongoDB connection failed: {e}")
        return None


def get_all_applications() -> pd.DataFrame:
    """Fetch all applications from MongoDB."""
    collection = init_mongo()
    if collection is None:
        return pd.DataFrame()

    applications = list(collection.find({}))
    if not applications:
        return pd.DataFrame()

    df = pd.DataFrame(applications)
    df['_id'] = df['_id'].astype(str)
    return df


# =============================================================================
# Authentication
# =============================================================================

def check_password() -> bool:
    """Returns True if the user has the correct password."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')

    if not admin_password_hash:
        # Default password: "admin123"
        admin_password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

    def get_password_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Show login form
    st.title("FGN Savings Bond Admin Dashboard")
    st.subheader("Admin Login")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if username == admin_username and get_password_hash(password) == admin_password_hash:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    return False

    return False


# =============================================================================
# Dashboard View
# =============================================================================

def view_dashboard():
    """Render the main dashboard with analytics."""
    st.header("Subscription Dashboard")

    # Get subscription summary
    form_handler = FormHandler()
    summary = form_handler.get_subscription_summary()

    # Overall summary metrics
    st.subheader("Overall Summary")
    col1, col2, col3, col4 = st.columns(4)

    wow_growth = summary.get('wow_growth', 0)
    growth_text = f"{wow_growth:+.1f}%" if wow_growth != 0 else "0%"

    col1.metric(
        "Total Applications",
        f"{summary['total_applications']:,}",
        delta=growth_text,
    )
    col2.metric("Total Value", f"₦{summary['total_value']:,.2f}")
    col3.metric("Average Value", f"₦{summary['average_value']:,.2f}" if summary['total_applications'] > 0 else "₦0.00")

    # Calculate additional metrics
    df = get_all_applications()
    if not df.empty and 'submission_date' in df.columns:
        # This month's applications
        current_month = datetime.now().strftime('%B')
        month_count = len(df[df.get('month_of_offer', '') == current_month]) if 'month_of_offer' in df.columns else 0
        col4.metric("This Month", f"{month_count:,}")

    st.divider()

    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Applicant Analysis",
        "Value Analysis",
        "Time Trends",
        "Top Applicants"
    ])

    with tab1:
        render_applicant_analysis(summary)

    with tab2:
        render_value_analysis(summary)

    with tab3:
        render_time_trends(summary)

    with tab4:
        render_top_applicants(summary)


def render_applicant_analysis(summary: dict):
    """Render applicant type analysis."""
    col1, col2 = st.columns(2)

    with col1:
        if summary['applicant_types']:
            st.subheader("Applications by Type")
            type_df = pd.DataFrame({
                'Type': list(summary['applicant_types'].keys()),
                'Count': list(summary['applicant_types'].values())
            })
            st.bar_chart(type_df.set_index('Type'))

            # Show percentages
            total = type_df['Count'].sum()
            type_df['Percentage'] = (type_df['Count'] / total * 100).round(1).astype(str) + '%'
            st.dataframe(type_df, use_container_width=True, hide_index=True)

    with col2:
        if summary['months']:
            st.subheader("Applications by Month")
            month_df = pd.DataFrame({
                'Month': list(summary['months'].keys()),
                'Count': list(summary['months'].values())
            })
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_df['MonthOrder'] = month_df['Month'].apply(
                lambda x: month_order.index(x) if x in month_order else 999
            )
            month_df = month_df.sort_values('MonthOrder')
            st.bar_chart(month_df.set_index('Month')['Count'])


def render_value_analysis(summary: dict):
    """Render bond value analysis."""
    if not summary['value_distribution']:
        st.info("No value distribution data available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Bond Value Distribution")
        value_df = pd.DataFrame({
            'Range': list(summary['value_distribution'].keys()),
            'Count': list(summary['value_distribution'].values())
        })

        range_order = [
            "₦0 - ₦10,000",
            "₦10,000 - ₦50,000",
            "₦50,000 - ₦100,000",
            "₦100,000 - ₦500,000",
            "₦500,000 - ₦1,000,000",
            "₦1,000,000+"
        ]
        range_order_dict = {r: i for i, r in enumerate(range_order)}
        value_df['RangeOrder'] = value_df['Range'].map(range_order_dict)
        value_df = value_df.sort_values('RangeOrder')

        st.bar_chart(value_df.set_index('Range')['Count'])

    with col2:
        st.subheader("Distribution (Pie Chart)")
        try:
            import plotly.express as px
            fig = px.pie(
                value_df,
                values='Count',
                names='Range',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            # True fallback using native Streamlit chart
            st.warning("Plotly not available. Showing basic chart.")
            st.bar_chart(value_df.set_index('Range')['Count'])


def render_time_trends(summary: dict):
    """Render time-based trend analysis."""
    if not summary['daily_trend']:
        st.info("No trend data available.")
        return

    st.subheader("Daily Application Trend")
    trend_df = pd.DataFrame({
        'Date': list(summary['daily_trend'].keys()),
        'Applications': list(summary['daily_trend'].values())
    })

    trend_df['Date'] = pd.to_datetime(trend_df['Date'])
    trend_df = trend_df.sort_values('Date')
    trend_df['Date_str'] = trend_df['Date'].dt.strftime('%Y-%m-%d')

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(trend_df.set_index('Date_str')['Applications'])

    with col2:
        if len(trend_df) > 7:
            st.subheader("7-Day Moving Average")
            trend_df['7-Day Average'] = trend_df['Applications'].rolling(7).mean()
            st.line_chart(trend_df.set_index('Date_str')['7-Day Average'].dropna())
        else:
            st.info("Need more than 7 days of data for moving average.")


def render_top_applicants(summary: dict):
    """Render top applicants by bond value."""
    if not summary['top_applicants']:
        st.info("No applicant data available.")
        return

    st.subheader("Top 5 Applicants by Bond Value")

    top_df = pd.DataFrame(summary['top_applicants'])
    top_df['Formatted Value'] = top_df['value'].apply(lambda x: f"₦{x:,.2f}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.table(top_df[['name', 'type', 'Formatted Value', 'date']].rename(columns={
            'name': 'Name/Company',
            'type': 'Type',
            'Formatted Value': 'Bond Value',
            'date': 'Submission Date'
        }))

    with col2:
        st.bar_chart(top_df.set_index('name')['value'])


# =============================================================================
# View Submissions (Enhanced with Filters and Pagination)
# =============================================================================

def view_submissions():
    """Render submissions view with advanced filtering and pagination."""
    st.header("Submitted Applications")

    # Get all applications
    df = get_all_applications()

    if df.empty:
        st.info("No applications submitted yet.")
        return

    # Render filter panel
    filter_panel = FilterPanel(key_prefix="submissions")
    filter_state = filter_panel.render(show_expanded=False)

    # Apply filters
    filtered_df = apply_filters(df, filter_state)

    # Show filter results count
    st.info(f"Showing {len(filtered_df):,} of {len(df):,} applications")

    # Prepare display columns
    display_df = filtered_df.copy()
    if 'applicant_type' in display_df.columns:
        display_df['Name/Company'] = display_df.apply(
            lambda x: x.get('company_name', '') if x.get('applicant_type') == 'Corporate'
            else x.get('full_name', ''),
            axis=1
        )

    # Define display columns
    display_columns = ['submission_date', 'applicant_type', 'Name/Company', 'tenor', 'bond_value', 'is_resident']
    available_columns = [c for c in display_columns if c in display_df.columns]

    # Format functions for display
    format_functions = {
        'bond_value': lambda x: f"₦{x:,.2f}" if pd.notna(x) else '',
        'is_resident': lambda x: 'Resident' if x else 'Non-Resident' if pd.notna(x) else '',
    }

    # Render paginated table
    st.subheader("Applications")
    render_paginated_table(
        df=display_df,
        key_prefix="submissions_table",
        display_columns=available_columns,
        format_functions=format_functions,
    )

    st.divider()

    # Export section
    export_manager = ExportManager(filtered_df, title="Bond Applications")
    export_manager.render_export_buttons(key_prefix="submissions_export")


# =============================================================================
# Application Details
# =============================================================================

def view_application_details():
    """Render individual application details view."""
    st.header("Application Details")

    collection = init_mongo()
    if collection is None:
        st.error("Database connection not available.")
        return

    applications = list(collection.find({}, {
        '_id': 1, 'full_name': 1, 'company_name': 1, 'applicant_type': 1, 'submission_date': 1
    }))

    if not applications:
        st.info("No applications available.")
        return

    # Create options for selectbox
    options = []
    for app in applications:
        name = app.get('company_name', '') if app.get('applicant_type') == 'Corporate' else app.get('full_name', '')
        date = app.get('submission_date', '')[:10] if app.get('submission_date') else ''
        options.append(f"{name} - {date} ({app['_id']})")

    selected = st.selectbox("Select Application", options)

    if selected:
        app_id = selected.split('(')[-1].replace(')', '')
        application = collection.find_one({'_id': app_id})

        if application:
            # Display in columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Application Information")
                st.write(f"**Submission Date:** {application.get('submission_date', 'N/A')}")
                st.write(f"**Applicant Type:** {application.get('applicant_type', 'N/A')}")
                st.write(f"**Tenor:** {application.get('tenor', 'N/A')}")
                st.write(f"**Bond Value:** ₦{application.get('bond_value', 0):,.2f}")
                st.write(f"**Amount in Words:** {application.get('amount_in_words', 'N/A')}")

                if application.get('applicant_type') in ['Individual', 'Joint']:
                    st.divider()
                    st.write(f"**Name:** {application.get('full_name', 'N/A')}")
                    st.write(f"**Email:** {application.get('email', 'N/A')}")
                    st.write(f"**Phone:** {application.get('phone_number', 'N/A')}")
                    st.write(f"**Occupation:** {application.get('occupation', 'N/A')}")
                else:
                    st.divider()
                    st.write(f"**Company:** {application.get('company_name', 'N/A')}")
                    st.write(f"**RC Number:** {application.get('rc_number', 'N/A')}")
                    st.write(f"**Contact Person:** {application.get('contact_person', 'N/A')}")

            with col2:
                st.subheader("Bank Details")
                st.write(f"**Bank Name:** {application.get('bank_name', 'N/A')}")
                st.write(f"**Account Number:** {application.get('account_number', 'N/A')}")
                st.write(f"**BVN:** {application.get('bvn', 'N/A')}")

                st.divider()
                st.subheader("Classification")
                residency = "Resident" if application.get('is_resident', True) else "Non-Resident"
                st.write(f"**Residency Status:** {residency}")
                categories = application.get('investor_category', [])
                st.write(f"**Investor Categories:** {', '.join(categories) if categories else 'N/A'}")

            st.divider()

            # Generate and display PDF
            st.subheader("Application PDF")
            form_handler = FormHandler()

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                form_handler.generate_pdf(application, tmp.name)
                with open(tmp.name, "rb") as f:
                    pdf_bytes = f.read()

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"application_{app_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            # PDF preview
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)


# =============================================================================
# Monthly Reports (Enhanced)
# =============================================================================

def generate_monthly_report():
    """Render monthly report generation view."""
    st.header("Monthly Subscription Report")

    # Report parameters form
    with st.form("report_parameters"):
        col1, col2, col3 = st.columns(3)

        current_year = datetime.now().year
        current_month = datetime.now().month

        with col1:
            year = st.selectbox(
                "Select Year",
                [current_year, current_year - 1, current_year - 2],
                index=0
            )

        with col2:
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            month = st.selectbox(
                "Select Month",
                range(1, 13),
                format_func=lambda x: months[x-1],
                index=current_month - 1
            )

        with col3:
            st.write("")
            st.write("")
            submit = st.form_submit_button("Generate Report", use_container_width=True)

    if submit or ('report_year' in st.session_state and 'report_month' in st.session_state):
        if submit:
            st.session_state.report_year = year
            st.session_state.report_month = month
        else:
            year = st.session_state.report_year
            month = st.session_state.report_month

        # Generate report
        form_handler = FormHandler()
        report_df = form_handler.get_monthly_report(year, month)

        if report_df.empty:
            st.info(f"No applications found for {months[month-1]} {year}")
            return

        st.divider()

        # Summary metrics
        st.subheader(f"Summary for {months[month-1]} {year}")

        total_applications = len(report_df)
        total_value = report_df['bond_value'].sum() if 'bond_value' in report_df.columns else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Applications", f"{total_applications:,}")
        col2.metric("Total Value", f"₦{total_value:,.2f}")
        if total_applications > 0:
            col3.metric("Average Value", f"₦{total_value/total_applications:,.2f}")

        # By type breakdown
        if 'applicant_type' in report_df.columns:
            type_counts = report_df['applicant_type'].value_counts()
            col4.metric("Applicant Types", f"{len(type_counts)}")

        st.divider()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            if 'applicant_type' in report_df.columns:
                st.subheader("Applications by Type")
                st.bar_chart(report_df['applicant_type'].value_counts())

        with col2:
            if 'tenor' in report_df.columns:
                st.subheader("Applications by Tenor")
                st.bar_chart(report_df['tenor'].value_counts())

        st.divider()

        # Detailed data with pagination
        st.subheader("Detailed Report")

        # Prepare display DataFrame
        display_df = report_df.copy()
        if 'applicant_type' in display_df.columns:
            display_df['Name/Company'] = display_df.apply(
                lambda x: x.get('company_name', '') if x.get('applicant_type') == 'Corporate'
                else x.get('full_name', ''),
                axis=1
            )

        display_columns = ['submission_date', 'applicant_type', 'Name/Company', 'tenor', 'bond_value']
        available_columns = [c for c in display_columns if c in display_df.columns]

        format_functions = {
            'bond_value': lambda x: f"₦{x:,.2f}" if pd.notna(x) else '',
        }

        render_paginated_table(
            df=display_df,
            key_prefix="report_table",
            display_columns=available_columns,
            format_functions=format_functions,
        )

        st.divider()

        # Export options
        export_manager = ExportManager(report_df, title=f"Bond Report {months[month-1]} {year}")
        export_manager.render_export_buttons(key_prefix="report_export")


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    if not check_password():
        return

    st.title("FGN Savings Bond Admin Dashboard")

    # Navigation sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "View Submissions", "Application Details", "Monthly Reports"],
        label_visibility="collapsed"
    )

    # Render selected page
    if page == "Dashboard":
        view_dashboard()
    elif page == "View Submissions":
        view_submissions()
    elif page == "Application Details":
        view_application_details()
    elif page == "Monthly Reports":
        generate_monthly_report()

    # Sidebar info and logout
    st.sidebar.divider()
    st.sidebar.caption("FGN Savings Bond System")
    st.sidebar.caption(f"Logged in as: {os.getenv('ADMIN_USERNAME', 'admin')}")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()


if __name__ == "__main__":
    main()
