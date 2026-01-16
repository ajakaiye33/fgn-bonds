"""
Advanced Filter Panel

Provides comprehensive filtering capabilities for the admin dashboard.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class FilterState:
    """Holds the current state of all filters."""
    date_range: Tuple[datetime, datetime] = None
    applicant_types: List[str] = field(default_factory=list)
    value_min: float = 0.0
    value_max: float = 50_000_000.0
    search_term: str = ""
    tenor: List[str] = field(default_factory=list)
    residency: Optional[str] = None
    month_of_offer: List[str] = field(default_factory=list)

    def is_active(self) -> bool:
        """Check if any filters are active."""
        return (
            self.date_range is not None or
            len(self.applicant_types) > 0 or
            self.value_min > 0 or
            self.value_max < 50_000_000 or
            self.search_term != "" or
            len(self.tenor) > 0 or
            self.residency is not None or
            len(self.month_of_offer) > 0
        )

    def clear(self):
        """Reset all filters to defaults."""
        self.date_range = None
        self.applicant_types = []
        self.value_min = 0.0
        self.value_max = 50_000_000.0
        self.search_term = ""
        self.tenor = []
        self.residency = None
        self.month_of_offer = []


class FilterPanel:
    """
    Advanced filter panel component for the admin dashboard.
    """

    APPLICANT_TYPES = ["Individual", "Joint", "Corporate"]
    TENORS = ["2-Year", "3-Year"]
    MONTHS = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    RESIDENCY_OPTIONS = ["All", "Resident", "Non-Resident"]

    def __init__(self, key_prefix: str = "filter"):
        """
        Initialize the filter panel.

        Args:
            key_prefix: Prefix for session state keys to avoid conflicts
        """
        self.key_prefix = key_prefix
        self._init_session_state()

    def _init_session_state(self):
        """Initialize filter state in session."""
        state_key = f"{self.key_prefix}_state"
        if state_key not in st.session_state:
            st.session_state[state_key] = FilterState()

    @property
    def state(self) -> FilterState:
        """Get current filter state."""
        return st.session_state[f"{self.key_prefix}_state"]

    @state.setter
    def state(self, value: FilterState):
        """Set filter state."""
        st.session_state[f"{self.key_prefix}_state"] = value

    def render(self, show_expanded: bool = True) -> FilterState:
        """
        Render the filter panel.

        Args:
            show_expanded: Whether to show the filter panel expanded by default

        Returns:
            Current FilterState after user interaction
        """
        with st.expander("Advanced Filters", expanded=show_expanded):
            self._render_filters()

        return self.state

    def _render_filters(self):
        """Render all filter controls."""
        # Row 1: Date Range and Search
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Date Range")
            date_col1, date_col2 = st.columns(2)

            # Default date range: last 30 days to today
            default_end = datetime.now()
            default_start = default_end - timedelta(days=30)

            with date_col1:
                start_date = st.date_input(
                    "From",
                    value=self.state.date_range[0] if self.state.date_range else default_start,
                    key=f"{self.key_prefix}_start_date"
                )

            with date_col2:
                end_date = st.date_input(
                    "To",
                    value=self.state.date_range[1] if self.state.date_range else default_end,
                    key=f"{self.key_prefix}_end_date"
                )

            # Quick date range buttons
            quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
            with quick_col1:
                if st.button("Today", key=f"{self.key_prefix}_today"):
                    start_date = datetime.now().date()
                    end_date = datetime.now().date()
            with quick_col2:
                if st.button("Last 7 Days", key=f"{self.key_prefix}_7days"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=7)
            with quick_col3:
                if st.button("Last 30 Days", key=f"{self.key_prefix}_30days"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=30)
            with quick_col4:
                if st.button("All Time", key=f"{self.key_prefix}_alltime"):
                    start_date = None
                    end_date = None

            if start_date and end_date:
                self.state.date_range = (
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
            else:
                self.state.date_range = None

        with col2:
            st.subheader("Text Search")
            search_term = st.text_input(
                "Search by name, company, email, or phone",
                value=self.state.search_term,
                placeholder="Enter search term...",
                key=f"{self.key_prefix}_search"
            )
            self.state.search_term = search_term

            st.caption("Searches across: Full Name, Company Name, Email, Phone Number")

        st.divider()

        # Row 2: Applicant Type and Tenor
        col3, col4, col5 = st.columns(3)

        with col3:
            st.subheader("Applicant Type")
            applicant_types = st.multiselect(
                "Select types",
                options=self.APPLICANT_TYPES,
                default=self.state.applicant_types if self.state.applicant_types else [],
                key=f"{self.key_prefix}_applicant_types"
            )
            self.state.applicant_types = applicant_types

        with col4:
            st.subheader("Tenor")
            tenors = st.multiselect(
                "Select tenors",
                options=self.TENORS,
                default=self.state.tenor if self.state.tenor else [],
                key=f"{self.key_prefix}_tenor"
            )
            self.state.tenor = tenors

        with col5:
            st.subheader("Residency Status")
            residency = st.selectbox(
                "Select status",
                options=self.RESIDENCY_OPTIONS,
                index=self.RESIDENCY_OPTIONS.index(self.state.residency) if self.state.residency else 0,
                key=f"{self.key_prefix}_residency"
            )
            self.state.residency = residency if residency != "All" else None

        st.divider()

        # Row 3: Value Range and Month of Offer
        col6, col7 = st.columns(2)

        with col6:
            st.subheader("Bond Value Range")
            value_range = st.slider(
                "Select range (in Naira)",
                min_value=0,
                max_value=50_000_000,
                value=(int(self.state.value_min), int(self.state.value_max)),
                step=5000,
                format="₦%d",
                key=f"{self.key_prefix}_value_range"
            )
            self.state.value_min = float(value_range[0])
            self.state.value_max = float(value_range[1])

            # Display formatted range
            st.caption(f"Range: ₦{value_range[0]:,.0f} - ₦{value_range[1]:,.0f}")

        with col7:
            st.subheader("Month of Offer")
            months = st.multiselect(
                "Select months",
                options=self.MONTHS,
                default=self.state.month_of_offer if self.state.month_of_offer else [],
                key=f"{self.key_prefix}_months"
            )
            self.state.month_of_offer = months

        # Filter actions
        st.divider()
        action_col1, action_col2, action_col3 = st.columns([1, 1, 2])

        with action_col1:
            if st.button("Clear All Filters", type="secondary", key=f"{self.key_prefix}_clear"):
                self.state.clear()
                st.rerun()

        with action_col2:
            if self.state.is_active():
                st.success("Filters active")
            else:
                st.info("No filters applied")

        with action_col3:
            if self.state.is_active():
                active_filters = []
                if self.state.date_range:
                    active_filters.append("Date Range")
                if self.state.applicant_types:
                    active_filters.append(f"Types: {', '.join(self.state.applicant_types)}")
                if self.state.value_min > 0 or self.state.value_max < 50_000_000:
                    active_filters.append("Value Range")
                if self.state.search_term:
                    active_filters.append(f"Search: '{self.state.search_term}'")
                if self.state.tenor:
                    active_filters.append(f"Tenor: {', '.join(self.state.tenor)}")
                if self.state.residency:
                    active_filters.append(f"Residency: {self.state.residency}")
                if self.state.month_of_offer:
                    active_filters.append(f"Months: {', '.join(self.state.month_of_offer)}")

                st.caption("Active: " + " | ".join(active_filters))


def render_filter_panel(key_prefix: str = "filter", show_expanded: bool = True) -> FilterState:
    """
    Convenience function to render a filter panel.

    Args:
        key_prefix: Prefix for session state keys
        show_expanded: Whether to show expanded by default

    Returns:
        Current FilterState
    """
    panel = FilterPanel(key_prefix)
    return panel.render(show_expanded)


def apply_filters(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    """
    Apply filter state to a DataFrame.

    Args:
        df: DataFrame to filter
        filters: FilterState with active filters

    Returns:
        Filtered DataFrame
    """
    if df.empty or not filters.is_active():
        return df

    result = df.copy()

    # Date range filter
    if filters.date_range and 'submission_date' in result.columns:
        start_date, end_date = filters.date_range

        # Convert submission_date to datetime if it's a string
        if result['submission_date'].dtype == 'object':
            # Handle various date formats
            def parse_date(date_str):
                if pd.isna(date_str):
                    return None
                try:
                    # Try ISO format first
                    return pd.to_datetime(date_str)
                except:
                    return None

            result['_parsed_date'] = result['submission_date'].apply(parse_date)
            result = result[
                (result['_parsed_date'] >= start_date) &
                (result['_parsed_date'] <= end_date)
            ]
            result = result.drop(columns=['_parsed_date'])
        else:
            result = result[
                (result['submission_date'] >= start_date) &
                (result['submission_date'] <= end_date)
            ]

    # Applicant type filter
    if filters.applicant_types and 'applicant_type' in result.columns:
        result = result[result['applicant_type'].isin(filters.applicant_types)]

    # Value range filter
    if 'bond_value' in result.columns:
        result = result[
            (result['bond_value'] >= filters.value_min) &
            (result['bond_value'] <= filters.value_max)
        ]

    # Text search filter
    if filters.search_term:
        search_lower = filters.search_term.lower()
        search_columns = ['full_name', 'company_name', 'email', 'phone_number', 'corp_email', 'corp_phone_number']

        # Build search mask
        mask = pd.Series([False] * len(result), index=result.index)
        for col in search_columns:
            if col in result.columns:
                col_mask = result[col].fillna('').astype(str).str.lower().str.contains(search_lower, na=False)
                mask = mask | col_mask

        result = result[mask]

    # Tenor filter
    if filters.tenor and 'tenor' in result.columns:
        result = result[result['tenor'].isin(filters.tenor)]

    # Residency filter
    if filters.residency and 'is_resident' in result.columns:
        is_resident_value = filters.residency == "Resident"
        result = result[result['is_resident'] == is_resident_value]

    # Month of offer filter
    if filters.month_of_offer and 'month_of_offer' in result.columns:
        result = result[result['month_of_offer'].isin(filters.month_of_offer)]

    return result
