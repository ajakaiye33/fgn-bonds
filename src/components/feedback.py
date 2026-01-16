"""
Feedback Components

Loading spinners, success animations, and error messages.
"""

import streamlit as st
from typing import Optional
import time


def show_loading_spinner(message: str = "Processing...", key: str = "loading"):
    """
    Display a loading spinner with message.

    Usage:
        with show_loading_spinner("Generating PDF..."):
            # Long running operation
            generate_pdf()
    """
    return st.spinner(message)


def show_success_message(
    message: str,
    title: str = "Success",
    icon: str = "check_circle",
    auto_dismiss: bool = False,
    dismiss_seconds: int = 3,
):
    """
    Display a success message with optional auto-dismiss.

    Args:
        message: Success message text
        title: Message title
        icon: Icon name (streamlit icon)
        auto_dismiss: Whether to auto-dismiss the message
        dismiss_seconds: Seconds before dismissing
    """
    st.success(f"**{title}**\n\n{message}")

    if auto_dismiss:
        time.sleep(dismiss_seconds)
        st.rerun()


def show_error_message(
    message: str,
    title: str = "Error",
    errors: list = None,
    show_retry: bool = False,
    retry_callback=None,
):
    """
    Display an error message with optional error list.

    Args:
        message: Error message text
        title: Message title
        errors: List of specific errors
        show_retry: Whether to show retry button
        retry_callback: Function to call on retry
    """
    st.error(f"**{title}**\n\n{message}")

    if errors:
        with st.expander("See details"):
            for error in errors:
                st.write(f"- {error}")

    if show_retry and retry_callback:
        if st.button("Retry", key="retry_btn"):
            retry_callback()


def show_warning_message(message: str, title: str = "Warning"):
    """Display a warning message."""
    st.warning(f"**{title}**\n\n{message}")


def show_info_card(
    title: str,
    content: str,
    icon: str = "info",
    color: str = "blue",
):
    """
    Display an info card with styled content.
    Uses native Streamlit components for better theme compatibility.

    Args:
        title: Card title
        content: Card content
        icon: Icon to display
        color: Card accent color (blue, green, yellow, red)
    """
    # Use native Streamlit callouts based on color
    if color == "green":
        st.success(f"**{title}**\n\n{content}")
    elif color == "yellow":
        st.warning(f"**{title}**\n\n{content}")
    elif color == "red":
        st.error(f"**{title}**\n\n{content}")
    else:  # blue/default
        st.info(f"**{title}**\n\n{content}")


def show_step_instructions(step_name: str, instructions: list):
    """
    Display instructions for a wizard step.

    Args:
        step_name: Name of the current step
        instructions: List of instruction strings
    """
    st.markdown(f"### {step_name}")

    for i, instruction in enumerate(instructions, 1):
        st.markdown(f"{i}. {instruction}")


def show_form_summary(data: dict, title: str = "Review Your Information"):
    """
    Display a summary of form data for review.

    Args:
        data: Dictionary of form data
        title: Summary title
    """
    st.markdown(f"### {title}")

    # Group data by sections
    sections = {
        "Bond Details": ["tenor", "bond_value", "amount_in_words", "month_of_offer"],
        "Personal Information": ["title", "full_name", "email", "phone_number", "date_of_birth"],
        "Bank Details": ["bank_name", "account_number", "bvn"],
        "Other": [],  # Catch-all for remaining fields
    }

    for section_name, fields in sections.items():
        with st.expander(section_name, expanded=True):
            for field in fields:
                if field in data and data[field]:
                    # Format field name for display
                    display_name = field.replace("_", " ").title()
                    st.write(f"**{display_name}:** {data[field]}")


def show_validation_summary(errors: list, warnings: list = None):
    """
    Display a summary of validation issues.

    Args:
        errors: List of error messages
        warnings: List of warning messages
    """
    if errors:
        st.error("**Please fix the following errors:**")
        for error in errors:
            st.markdown(f"- {error}")

    if warnings:
        st.warning("**Warnings:**")
        for warning in warnings:
            st.markdown(f"- {warning}")


def show_progress_toast(message: str, progress: float):
    """
    Display a progress toast notification.

    Args:
        message: Progress message
        progress: Progress value (0-1)
    """
    progress_bar = st.progress(progress)
    st.caption(message)
    return progress_bar


def show_status(label: str, expanded: bool = True):
    """
    Create a native Streamlit status container for multi-step operations.

    Usage:
        with show_status("Processing...") as status:
            st.write("Step 1: Validating...")
            # do validation
            st.write("Step 2: Saving...")
            # do save
            status.update(label="Complete!", state="complete")

    Args:
        label: Initial status label
        expanded: Whether to show expanded details

    Returns:
        Streamlit status container
    """
    return st.status(label, expanded=expanded)
