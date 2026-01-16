"""
Accessibility Module

WCAG 2.1 AA compliance utilities for the FGN Savings Bond application.
Provides ARIA labels, screen reader support, and keyboard navigation helpers.
"""

import streamlit as st
from typing import Optional, Dict, Any


def inject_accessibility_css():
    """
    Inject accessibility-focused CSS into the Streamlit app.
    Includes focus indicators, skip links, screen reader utilities, and high contrast support.
    """
    st.markdown("""
    <style>
    /* ============================================
       ACCESSIBILITY CSS - WCAG 2.1 AA Compliance
       ============================================ */

    /* Skip to Main Content Link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #006400;
        color: white;
        padding: 8px 16px;
        z-index: 10000;
        text-decoration: none;
        font-weight: 600;
        border-radius: 0 0 4px 0;
        transition: top 0.3s ease;
    }

    .skip-link:focus {
        top: 0;
        outline: 3px solid #4CAF50;
        outline-offset: 2px;
    }

    /* Focus Indicators - Enhanced visibility */
    *:focus-visible {
        outline: 3px solid #4CAF50 !important;
        outline-offset: 2px !important;
    }

    /* Remove default focus for mouse users */
    *:focus:not(:focus-visible) {
        outline: none;
    }

    /* Button Focus States */
    button:focus-visible,
    .stButton > button:focus-visible,
    [role="button"]:focus-visible {
        outline: 3px solid #4CAF50 !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.3) !important;
    }

    /* Input Focus States */
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible,
    .stTextInput input:focus-visible,
    .stTextArea textarea:focus-visible,
    .stSelectbox select:focus-visible {
        outline: 3px solid #4CAF50 !important;
        outline-offset: 0 !important;
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
    }

    /* Link Focus States */
    a:focus-visible {
        outline: 3px solid #4CAF50 !important;
        outline-offset: 2px !important;
        text-decoration: underline !important;
    }

    /* Screen Reader Only - Hidden but accessible */
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }

    /* Screen Reader Only - Focusable (shows on focus) */
    .sr-only-focusable:focus,
    .sr-only-focusable:active {
        position: static !important;
        width: auto !important;
        height: auto !important;
        padding: inherit !important;
        margin: inherit !important;
        overflow: visible !important;
        clip: auto !important;
        white-space: normal !important;
    }

    /* Ensure minimum touch target size (44x44px) */
    button,
    [role="button"],
    input[type="checkbox"],
    input[type="radio"],
    .stButton > button,
    .stCheckbox,
    .stRadio label {
        min-height: 44px;
        min-width: 44px;
    }

    /* Improve checkbox/radio touch targets */
    .stCheckbox > label,
    .stRadio > label {
        padding: 8px 12px;
        display: flex;
        align-items: center;
        min-height: 44px;
    }

    /* High Contrast Mode Support */
    @media (prefers-contrast: high) {
        * {
            border-color: currentColor !important;
        }

        button,
        .stButton > button {
            border: 2px solid currentColor !important;
        }

        input,
        textarea,
        select {
            border: 2px solid currentColor !important;
        }

        a {
            text-decoration: underline !important;
        }
    }

    /* Reduced Motion Support */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* Color Contrast Improvements */
    /* Ensure text has sufficient contrast (4.5:1 for normal, 3:1 for large) */
    .low-contrast-fix {
        color: #1a1a1a !important;
    }

    /* Error states with accessible colors */
    .error-text {
        color: #d32f2f !important;
        font-weight: 500;
    }

    .success-text {
        color: #2e7d32 !important;
        font-weight: 500;
    }

    .warning-text {
        color: #ed6c02 !important;
        font-weight: 500;
    }

    /* Ensure links are distinguishable */
    a:not([class]) {
        color: #006400;
        text-decoration: underline;
    }

    a:not([class]):hover {
        color: #004d00;
        text-decoration: none;
    }

    /* Form Labels - Ensure association */
    label {
        display: block;
        margin-bottom: 4px;
        font-weight: 500;
    }

    /* Required Field Indicator */
    .required-indicator::after {
        content: " *";
        color: #d32f2f;
        font-weight: bold;
    }

    /* Error Message Styling */
    .field-error {
        color: #d32f2f;
        font-size: 0.875rem;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .field-error::before {
        content: "⚠";
    }

    /* Live Region for Announcements */
    .live-region {
        position: absolute;
        left: -10000px;
        width: 1px;
        height: 1px;
        overflow: hidden;
    }

    /* Progress Indicator Accessibility */
    [role="progressbar"] {
        position: relative;
    }

    /* Table Accessibility */
    table {
        border-collapse: collapse;
    }

    th {
        text-align: left;
        font-weight: 600;
        background-color: rgba(0, 100, 0, 0.1);
    }

    th, td {
        padding: 12px;
        border: 1px solid #ddd;
    }

    /* Caption for tables */
    caption {
        font-weight: 600;
        text-align: left;
        padding: 8px 0;
        caption-side: top;
    }

    /* Dialog/Modal Accessibility */
    [role="dialog"] {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1000;
        background: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        max-width: 90vw;
        max-height: 90vh;
        overflow: auto;
    }

    [role="dialog"]::backdrop {
        background: rgba(0, 0, 0, 0.5);
    }

    /* Tooltip Accessibility */
    [role="tooltip"] {
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.875rem;
        max-width: 300px;
        z-index: 1000;
    }

    /* Status Messages */
    [role="status"],
    [role="alert"] {
        padding: 12px 16px;
        border-radius: 4px;
        margin: 8px 0;
    }

    [role="alert"] {
        background-color: #ffebee;
        border-left: 4px solid #d32f2f;
    }

    [role="status"] {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }

    </style>
    """, unsafe_allow_html=True)


def add_skip_link(main_content_id: str = "main-content"):
    """
    Add a skip-to-content link for keyboard navigation.

    Args:
        main_content_id: ID of the main content container
    """
    st.markdown(f"""
    <a href="#{main_content_id}" class="skip-link">
        Skip to main content
    </a>
    """, unsafe_allow_html=True)


def add_main_landmark(content_id: str = "main-content"):
    """
    Add main content landmark for screen readers.

    Args:
        content_id: ID for the main content area
    """
    st.markdown(f"""
    <main id="{content_id}" role="main" aria-label="Main content">
    """, unsafe_allow_html=True)


def close_main_landmark():
    """Close the main content landmark."""
    st.markdown("</main>", unsafe_allow_html=True)


def announce_to_screen_reader(message: str, politeness: str = "polite"):
    """
    Announce a message to screen readers using ARIA live regions.

    Args:
        message: Message to announce
        politeness: 'polite' (waits for pause) or 'assertive' (interrupts)
    """
    st.markdown(f"""
    <div role="status" aria-live="{politeness}" aria-atomic="true" class="live-region">
        {message}
    </div>
    """, unsafe_allow_html=True)


def create_accessible_heading(
    text: str,
    level: int = 1,
    id: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Create an accessible heading with proper hierarchy.

    Args:
        text: Heading text
        level: Heading level (1-6)
        id: Optional ID for linking
        description: Optional description for screen readers
    """
    level = max(1, min(6, level))
    id_attr = f'id="{id}"' if id else ''
    aria_desc = f'aria-describedby="{id}-desc"' if description else ''

    st.markdown(f"""
    <h{level} {id_attr} {aria_desc}>{text}</h{level}>
    """, unsafe_allow_html=True)

    if description:
        st.markdown(f"""
        <p id="{id}-desc" class="sr-only">{description}</p>
        """, unsafe_allow_html=True)


def create_accessible_form_field(
    label: str,
    field_id: str,
    required: bool = False,
    error_message: Optional[str] = None,
    help_text: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate ARIA attributes for accessible form fields.

    Args:
        label: Field label
        field_id: Unique field identifier
        required: Whether the field is required
        error_message: Error message if validation failed
        help_text: Help text for the field

    Returns:
        Dictionary of ARIA attributes
    """
    attrs = {
        'aria-label': label,
        'id': field_id,
    }

    if required:
        attrs['aria-required'] = 'true'

    describedby = []
    if help_text:
        attrs['aria-describedby'] = f'{field_id}-help'
        describedby.append(f'{field_id}-help')

    if error_message:
        attrs['aria-invalid'] = 'true'
        attrs['aria-errormessage'] = f'{field_id}-error'
        describedby.append(f'{field_id}-error')

    if describedby:
        attrs['aria-describedby'] = ' '.join(describedby)

    return attrs


def render_accessible_error(field_id: str, error_message: str):
    """
    Render an accessible error message for a form field.

    Args:
        field_id: ID of the associated field
        error_message: Error message to display
    """
    st.markdown(f"""
    <div id="{field_id}-error" class="field-error" role="alert" aria-live="assertive">
        {error_message}
    </div>
    """, unsafe_allow_html=True)


def render_accessible_help(field_id: str, help_text: str):
    """
    Render accessible help text for a form field.

    Args:
        field_id: ID of the associated field
        help_text: Help text to display
    """
    st.markdown(f"""
    <div id="{field_id}-help" class="help-text">
        {help_text}
    </div>
    """, unsafe_allow_html=True)


def create_accessible_table_caption(caption: str, table_id: str):
    """
    Create an accessible table with caption.

    Args:
        caption: Table caption describing its content
        table_id: Unique table identifier
    """
    st.markdown(f"""
    <caption id="{table_id}-caption">{caption}</caption>
    """, unsafe_allow_html=True)


def get_color_contrast_ratio(foreground: str, background: str) -> float:
    """
    Calculate the contrast ratio between two colors.

    Args:
        foreground: Foreground color in hex (e.g., '#000000')
        background: Background color in hex (e.g., '#ffffff')

    Returns:
        Contrast ratio (1:1 to 21:1)
    """
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_luminance(rgb: tuple) -> float:
        r, g, b = [
            c / 255.0 if c / 255.0 <= 0.03928
            else ((c / 255.0 + 0.055) / 1.055) ** 2.4
            for c in rgb
        ]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    fg_luminance = get_luminance(hex_to_rgb(foreground))
    bg_luminance = get_luminance(hex_to_rgb(background))

    lighter = max(fg_luminance, bg_luminance)
    darker = min(fg_luminance, bg_luminance)

    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_contrast(
    foreground: str,
    background: str,
    level: str = "AA",
    large_text: bool = False
) -> bool:
    """
    Check if colors meet WCAG contrast requirements.

    Args:
        foreground: Foreground color in hex
        background: Background color in hex
        level: 'AA' or 'AAA'
        large_text: Whether the text is large (18pt+ or 14pt bold)

    Returns:
        True if contrast meets requirements
    """
    ratio = get_color_contrast_ratio(foreground, background)

    if level == "AAA":
        return ratio >= 4.5 if large_text else ratio >= 7.0
    else:  # AA
        return ratio >= 3.0 if large_text else ratio >= 4.5


def setup_accessibility():
    """
    Set up all accessibility features for the application.
    Call this at the start of your Streamlit app.
    """
    # CSS must be injected every render as Streamlit rebuilds the DOM on each rerun
    inject_accessibility_css()
    add_skip_link()
