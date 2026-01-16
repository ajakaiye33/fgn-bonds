"""
Pagination Component

Provides paginated data table functionality for handling large datasets.
"""

import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Callable
import math


@dataclass
class PaginationState:
    """Holds pagination state."""
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total_items == 0 or self.page_size == 0:
            return 1
        return math.ceil(self.total_items / self.page_size)

    @property
    def start_index(self) -> int:
        """Get the start index for the current page."""
        return (self.current_page - 1) * self.page_size

    @property
    def end_index(self) -> int:
        """Get the end index for the current page."""
        return min(self.start_index + self.page_size, self.total_items)

    def go_to_page(self, page: int):
        """Navigate to a specific page."""
        self.current_page = max(1, min(page, self.total_pages))

    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1

    def first_page(self):
        """Go to first page."""
        self.current_page = 1

    def last_page(self):
        """Go to last page."""
        self.current_page = self.total_pages


class PaginatedTable:
    """
    Paginated data table component.
    """

    PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 250]

    def __init__(self, key_prefix: str = "table"):
        """
        Initialize the paginated table.

        Args:
            key_prefix: Prefix for session state keys
        """
        self.key_prefix = key_prefix
        self._init_session_state()

    def _init_session_state(self):
        """Initialize pagination state in session."""
        state_key = f"{self.key_prefix}_pagination"
        if state_key not in st.session_state:
            st.session_state[state_key] = PaginationState()

    @property
    def state(self) -> PaginationState:
        """Get current pagination state."""
        return st.session_state[f"{self.key_prefix}_pagination"]

    @state.setter
    def state(self, value: PaginationState):
        """Set pagination state."""
        st.session_state[f"{self.key_prefix}_pagination"] = value

    def render(
        self,
        df: pd.DataFrame,
        display_columns: Optional[List[str]] = None,
        column_config: Optional[dict] = None,
        format_functions: Optional[dict] = None,
        show_index: bool = False,
        height: Optional[int] = None,
        on_row_click: Optional[Callable] = None,
    ) -> pd.DataFrame:
        """
        Render a paginated table.

        Args:
            df: DataFrame to display
            display_columns: List of columns to display (None = all)
            column_config: Streamlit column configuration dict
            format_functions: Dict mapping column names to format functions
            show_index: Whether to show the DataFrame index
            height: Fixed height for the table
            on_row_click: Callback when a row is clicked

        Returns:
            The currently displayed page DataFrame
        """
        if df.empty:
            st.info("No data to display.")
            return df

        # Update total items
        self.state.total_items = len(df)

        # Ensure current page is valid
        if self.state.current_page > self.state.total_pages:
            self.state.current_page = self.state.total_pages

        # Render pagination controls at top
        self._render_pagination_controls()

        # Get page slice
        page_df = df.iloc[self.state.start_index:self.state.end_index].copy()

        # Apply format functions
        if format_functions:
            for col, func in format_functions.items():
                if col in page_df.columns:
                    page_df[col] = page_df[col].apply(func)

        # Select display columns
        if display_columns:
            available_cols = [c for c in display_columns if c in page_df.columns]
            page_df = page_df[available_cols]

        # Render table
        if column_config:
            st.dataframe(
                page_df,
                use_container_width=True,
                hide_index=not show_index,
                column_config=column_config,
                height=height,
            )
        else:
            st.dataframe(
                page_df,
                use_container_width=True,
                hide_index=not show_index,
                height=height,
            )

        # Render pagination controls at bottom
        self._render_pagination_controls(position="bottom")

        return page_df

    def _render_pagination_controls(self, position: str = "top"):
        """Render pagination controls."""
        state = self.state
        key_suffix = f"_{position}"

        if position == "top":
            # Top controls: Page size and info
            col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

            with col1:
                page_size = st.selectbox(
                    "Per page",
                    options=self.PAGE_SIZE_OPTIONS,
                    index=self.PAGE_SIZE_OPTIONS.index(state.page_size)
                          if state.page_size in self.PAGE_SIZE_OPTIONS else 1,
                    key=f"{self.key_prefix}_page_size{key_suffix}",
                    label_visibility="collapsed"
                )
                if page_size != state.page_size:
                    state.page_size = page_size
                    state.first_page()
                    st.rerun()

            with col2:
                st.caption(f"Showing {state.start_index + 1}-{state.end_index} of {state.total_items}")

            with col4:
                # Quick jump to page
                if state.total_pages > 1:
                    page_num = st.number_input(
                        "Go to page",
                        min_value=1,
                        max_value=state.total_pages,
                        value=state.current_page,
                        key=f"{self.key_prefix}_goto{key_suffix}",
                        label_visibility="collapsed"
                    )
                    if page_num != state.current_page:
                        state.go_to_page(page_num)
                        st.rerun()

        else:
            # Bottom controls: Navigation buttons
            if state.total_pages > 1:
                nav_cols = st.columns([1, 1, 2, 1, 1])

                with nav_cols[0]:
                    if st.button("First", disabled=state.current_page == 1,
                                key=f"{self.key_prefix}_first{key_suffix}"):
                        state.first_page()
                        st.rerun()

                with nav_cols[1]:
                    if st.button("Previous", disabled=state.current_page == 1,
                                key=f"{self.key_prefix}_prev{key_suffix}"):
                        state.prev_page()
                        st.rerun()

                with nav_cols[2]:
                    # Page indicator with page numbers
                    self._render_page_numbers()

                with nav_cols[3]:
                    if st.button("Next", disabled=state.current_page == state.total_pages,
                                key=f"{self.key_prefix}_next{key_suffix}"):
                        state.next_page()
                        st.rerun()

                with nav_cols[4]:
                    if st.button("Last", disabled=state.current_page == state.total_pages,
                                key=f"{self.key_prefix}_last{key_suffix}"):
                        state.last_page()
                        st.rerun()

    def _render_page_numbers(self):
        """Render page number indicators."""
        state = self.state
        total_pages = state.total_pages
        current_page = state.current_page

        # Determine which pages to show
        if total_pages <= 7:
            pages = list(range(1, total_pages + 1))
        else:
            # Show first, last, and pages around current
            pages = set([1, total_pages])

            # Add pages around current
            for i in range(max(1, current_page - 1), min(total_pages + 1, current_page + 2)):
                pages.add(i)

            pages = sorted(pages)

            # Add ellipsis indicators
            final_pages = []
            prev_page = 0
            for page in pages:
                if page - prev_page > 1:
                    final_pages.append("...")
                final_pages.append(page)
                prev_page = page
            pages = final_pages

        # Render as text
        page_str = " ".join(
            f"**[{p}]**" if p == current_page else str(p)
            for p in pages
        )
        st.markdown(f"Pages: {page_str}", unsafe_allow_html=True)


def render_paginated_table(
    df: pd.DataFrame,
    key_prefix: str = "table",
    display_columns: Optional[List[str]] = None,
    column_config: Optional[dict] = None,
    format_functions: Optional[dict] = None,
    show_index: bool = False,
    height: Optional[int] = None,
) -> pd.DataFrame:
    """
    Convenience function to render a paginated table.

    Args:
        df: DataFrame to display
        key_prefix: Prefix for session state keys
        display_columns: Columns to display
        column_config: Streamlit column configuration
        format_functions: Format functions for columns
        show_index: Whether to show index
        height: Table height

    Returns:
        Currently displayed page DataFrame
    """
    table = PaginatedTable(key_prefix)
    return table.render(
        df=df,
        display_columns=display_columns,
        column_config=column_config,
        format_functions=format_functions,
        show_index=show_index,
        height=height,
    )
