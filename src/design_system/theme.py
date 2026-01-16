"""
Theme System

Provides theme application and CSS generation using design tokens.
Supports dark and light themes with consistent styling.
"""

import streamlit as st
from enum import Enum
from typing import Optional
from .tokens import Colors, Typography, Spacing, Shadows, BorderRadius, Transitions


class ThemeMode(Enum):
    """Theme mode options"""
    DARK = "dark"
    LIGHT = "light"


def get_google_fonts_import() -> str:
    """Get Google Fonts import statement"""
    return """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
"""


def get_css_variables(mode: ThemeMode) -> str:
    """Generate CSS custom properties based on theme mode"""
    palette = Colors.get_dark_palette() if mode == ThemeMode.DARK else Colors.get_light_palette()

    return f"""
:root {{
    /* Colors */
    --color-bg: {palette['bg']};
    --color-surface: {palette['surface']};
    --color-elevated: {palette['elevated']};
    --color-border: {palette['border']};
    --color-text: {palette['text']};
    --color-text-secondary: {palette['text_secondary']};
    --color-primary: {palette['primary']};
    --color-primary-hover: {palette['primary_hover']};
    --color-primary-dark: {palette['primary_dark']};

    /* Primary palette */
    --color-primary-50: {Colors.PRIMARY_50};
    --color-primary-100: {Colors.PRIMARY_100};
    --color-primary-500: {Colors.PRIMARY_500};
    --color-primary-700: {Colors.PRIMARY_700};
    --color-primary-900: {Colors.PRIMARY_900};

    /* Semantic colors */
    --color-success: {Colors.SUCCESS};
    --color-success-light: {Colors.SUCCESS_LIGHT};
    --color-error: {Colors.ERROR};
    --color-error-light: {Colors.ERROR_LIGHT};
    --color-warning: {Colors.WARNING};
    --color-warning-light: {Colors.WARNING_LIGHT};
    --color-info: {Colors.INFO};
    --color-info-light: {Colors.INFO_LIGHT};

    /* Typography */
    --font-family: {Typography.FONT_FAMILY};
    --font-family-mono: {Typography.FONT_FAMILY_MONO};
    --font-size-xs: {Typography.SIZE_XS};
    --font-size-sm: {Typography.SIZE_SM};
    --font-size-base: {Typography.SIZE_BASE};
    --font-size-lg: {Typography.SIZE_LG};
    --font-size-xl: {Typography.SIZE_XL};
    --font-size-2xl: {Typography.SIZE_2XL};
    --font-size-3xl: {Typography.SIZE_3XL};
    --font-size-4xl: {Typography.SIZE_4XL};

    /* Font weights */
    --font-weight-light: {Typography.WEIGHT_LIGHT};
    --font-weight-regular: {Typography.WEIGHT_REGULAR};
    --font-weight-medium: {Typography.WEIGHT_MEDIUM};
    --font-weight-semibold: {Typography.WEIGHT_SEMIBOLD};
    --font-weight-bold: {Typography.WEIGHT_BOLD};

    /* Spacing */
    --spacing-xs: {Spacing.XS};
    --spacing-sm: {Spacing.SM};
    --spacing-md: {Spacing.MD};
    --spacing-lg: {Spacing.LG};
    --spacing-xl: {Spacing.XL};
    --spacing-xxl: {Spacing.XXL};

    /* Border radius */
    --radius-sm: {BorderRadius.SM};
    --radius-md: {BorderRadius.MD};
    --radius-lg: {BorderRadius.LG};
    --radius-xl: {BorderRadius.XL};
    --radius-full: {BorderRadius.FULL};

    /* Shadows */
    --shadow-sm: {Shadows.SM};
    --shadow-md: {Shadows.MD};
    --shadow-lg: {Shadows.LG};
    --shadow-focus: {Shadows.FOCUS_PRIMARY};

    /* Transitions */
    --transition-fast: {Transitions.DURATION_FAST};
    --transition-base: {Transitions.DURATION_BASE};
    --transition-slow: {Transitions.DURATION_SLOW};
}}
"""


def get_base_styles(mode: ThemeMode) -> str:
    """Generate base styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Base styles */
.stApp {{
    background-color: var(--color-bg);
    font-family: var(--font-family);
}}

/* Hide Streamlit branding */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Main container styling */
.main .block-container {{
    padding-top: var(--spacing-lg);
    padding-bottom: var(--spacing-xxl);
    max-width: 1200px;
}}

/* Typography defaults */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-family);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
    line-height: {Typography.LINE_HEIGHT_TIGHT};
}}

h1 {{
    font-size: var(--font-size-3xl);
    margin-bottom: var(--spacing-lg);
}}

h2 {{
    font-size: var(--font-size-2xl);
    margin-bottom: var(--spacing-md);
}}

h3 {{
    font-size: var(--font-size-xl);
    margin-bottom: var(--spacing-md);
}}

p, span, label {{
    font-family: var(--font-family);
    color: var(--color-text);
    line-height: {Typography.LINE_HEIGHT_NORMAL};
}}

/* Links */
a {{
    color: var(--color-primary);
    text-decoration: none;
    transition: color var(--transition-fast);
}}

a:hover {{
    color: var(--color-primary-hover);
    text-decoration: underline;
}}
"""


def get_form_styles(mode: ThemeMode) -> str:
    """Generate form element styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Form field containers */
.stTextInput, .stSelectbox, .stNumberInput, .stDateInput, .stTextArea {{
    margin-bottom: var(--spacing-md);
}}

/* Input labels */
.stTextInput > label,
.stSelectbox > label,
.stNumberInput > label,
.stDateInput > label,
.stTextArea > label {{
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--color-text);
    margin-bottom: var(--spacing-xs);
}}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox > div > div {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    color: var(--color-text);
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: {Spacing.INPUT_PADDING_Y} {Spacing.INPUT_PADDING_X};
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}}

/* Input focus states */
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {{
    outline: none;
    border-color: var(--color-primary);
    box-shadow: var(--shadow-focus);
}}

/* Placeholder text */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: var(--color-text-secondary);
    opacity: 0.7;
}}

/* Radio buttons */
.stRadio > div {{
    display: flex;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
}}

.stRadio > div > label {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--font-size-base);
    color: var(--color-text);
    cursor: pointer;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    background-color: var(--color-surface);
    transition: all var(--transition-fast);
}}

.stRadio > div > label:hover {{
    border-color: var(--color-primary);
    background-color: var(--color-elevated);
}}

.stRadio > div > label[data-checked="true"] {{
    border-color: var(--color-primary);
    background-color: {'rgba(76, 175, 80, 0.15)' if is_dark else Colors.PRIMARY_50};
}}

/* Checkboxes */
.stCheckbox > label {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--font-size-base);
    color: var(--color-text);
    cursor: pointer;
}}

/* Select boxes */
.stSelectbox > div > div {{
    cursor: pointer;
}}

.stSelectbox [data-baseweb="select"] > div {{
    background-color: var(--color-surface);
    border-color: var(--color-border);
}}

.stSelectbox [data-baseweb="select"] > div:hover {{
    border-color: var(--color-primary);
}}

/* Selectbox selected value text - ensure visibility in dark mode */
/* Fix: The value div has height:2px which clips the text */
[data-baseweb="select"] div[value] {{
    height: auto !important;
    min-height: 24px !important;
    overflow: visible !important;
    color: #E6EDF3 !important;
    -webkit-text-fill-color: #E6EDF3 !important;
}}

/* Date picker calendar header buttons - month/year text visibility */
/* Fix: The buttons have width:44px which clips text like "January" */
[data-baseweb="calendar"] button {{
    width: auto !important;
    min-width: 44px !important;
    overflow: visible !important;
    padding: 4px 8px !important;
}}

/* Selectbox dropdown options */
[data-baseweb="popover"] [role="listbox"] [role="option"] {{
    color: var(--color-text);
    background-color: var(--color-surface);
}}

[data-baseweb="popover"] [role="listbox"] [role="option"]:hover {{
    background-color: var(--color-elevated);
}}

[data-baseweb="popover"] [role="listbox"] [role="option"][aria-selected="true"] {{
    background-color: var(--color-primary);
    color: white;
}}
"""


def get_button_styles(mode: ThemeMode) -> str:
    """Generate button styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Primary button */
.stButton > button {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: {Colors.WHITE};
    background-color: var(--color-primary);
    border: none;
    border-radius: var(--radius-md);
    padding: {Spacing.BUTTON_PADDING_Y} {Spacing.BUTTON_PADDING_X};
    cursor: pointer;
    transition: all var(--transition-fast);
    min-height: 44px;
}}

.stButton > button:hover {{
    background-color: var(--color-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}}

.stButton > button:active {{
    transform: translateY(0);
    box-shadow: none;
}}

.stButton > button:focus {{
    outline: none;
    box-shadow: var(--shadow-focus);
}}

.stButton > button:disabled {{
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}}

/* Form submit button */
.stForm [data-testid="stFormSubmitButton"] > button {{
    width: 100%;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    font-size: var(--font-size-lg);
    padding: var(--spacing-md) var(--spacing-xl);
}}

.stForm [data-testid="stFormSubmitButton"] > button:hover {{
    background: linear-gradient(135deg, var(--color-primary-hover) 0%, var(--color-primary) 100%);
}}

/* Download button */
.stDownloadButton > button {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--color-primary);
    background-color: transparent;
    border: 2px solid var(--color-primary);
    border-radius: var(--radius-md);
    padding: {Spacing.BUTTON_PADDING_Y} {Spacing.BUTTON_PADDING_X};
    transition: all var(--transition-fast);
}}

.stDownloadButton > button:hover {{
    color: {Colors.WHITE};
    background-color: var(--color-primary);
}}
"""


def get_card_styles(mode: ThemeMode) -> str:
    """Generate card and container styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Card containers */
div[data-testid="stExpander"] {{
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
}}

div[data-testid="stExpander"] > details > summary {{
    font-weight: var(--font-weight-semibold);
    padding: var(--spacing-md);
}}

/* Metric cards */
div[data-testid="stMetric"] {{
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
}}

div[data-testid="stMetric"] label {{
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-medium);
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text);
}}

div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
    font-size: var(--font-size-sm);
}}

/* Alert box base styling - target the actual container */
[data-testid="stAlertContainer"][data-baseweb="notification"] {{
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-md) !important;
    font-size: var(--font-size-sm) !important;
    background-color: {Colors.INFO_DARK if is_dark else Colors.INFO_LIGHT} !important;
    border-left: 4px solid var(--color-info) !important;
}}

/* Alert text color for dark mode readability */
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stAlert"] p,
[data-testid="stAlert"] li,
[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] li,
[data-testid="stAlertContainer"] strong {{
    color: {'#E6EDF3' if is_dark else '#1F2328'} !important;
}}

/* Success alert - uses positive kind */
.st-emotion-cache-15wn9x1 [data-testid="stAlertContainer"],
[data-testid="stAlertContainer"].stAlertContainer[class*="st-bf"],
.stSuccess [data-testid="stAlertContainer"] {{
    background-color: {Colors.SUCCESS_DARK if is_dark else Colors.SUCCESS_LIGHT} !important;
    border-left: 4px solid var(--color-success) !important;
}}

/* Warning alert */
.st-emotion-cache-1i1nsjt [data-testid="stAlertContainer"],
[data-testid="stAlertContainer"].stAlertContainer[class*="st-bd"],
.stWarning [data-testid="stAlertContainer"] {{
    background-color: {Colors.WARNING_DARK if is_dark else Colors.WARNING_LIGHT} !important;
    border-left: 4px solid var(--color-warning) !important;
}}

/* Error alert */
.st-emotion-cache-1gulkj5 [data-testid="stAlertContainer"],
[data-testid="stAlertContainer"].stAlertContainer[class*="st-bb"],
.stError [data-testid="stAlertContainer"] {{
    background-color: {Colors.ERROR_DARK if is_dark else Colors.ERROR_LIGHT} !important;
    border-left: 4px solid var(--color-error) !important;
}}

/* Info alert (default) */
.st-emotion-cache-p4rjtr [data-testid="stAlertContainer"],
[data-testid="stAlertContainer"].stAlertContainer[class*="st-bg"],
.stInfo [data-testid="stAlertContainer"] {{
    background-color: {Colors.INFO_DARK if is_dark else Colors.INFO_LIGHT} !important;
    border-left: 4px solid var(--color-info) !important;
}}
"""


def get_tab_styles(mode: ThemeMode) -> str:
    """Generate tab navigation styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Tab container */
.stTabs [data-baseweb="tab-list"] {{
    gap: var(--spacing-xs);
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xs);
}}

/* Individual tabs */
.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-secondary);
    background-color: transparent;
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-lg);
    transition: all var(--transition-fast);
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: var(--color-text);
    background-color: var(--color-elevated);
}}

.stTabs [aria-selected="true"] {{
    color: {Colors.WHITE} !important;
    background-color: var(--color-primary) !important;
}}

/* Tab content */
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: var(--spacing-lg);
}}
"""


def get_table_styles(mode: ThemeMode) -> str:
    """Generate table and dataframe styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Dataframe container */
.stDataFrame {{
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
}}

/* Table header */
.stDataFrame thead th {{
    background-color: {'var(--color-elevated)' if is_dark else Colors.NEUTRAL_100};
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
    padding: var(--spacing-sm) var(--spacing-md);
    border-bottom: 2px solid var(--color-border);
}}

/* Table cells */
.stDataFrame tbody td {{
    padding: var(--spacing-sm) var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
    color: var(--color-text);
}}

/* Table row hover */
.stDataFrame tbody tr:hover {{
    background-color: var(--color-elevated);
}}
"""


def get_sidebar_styles(mode: ThemeMode) -> str:
    """Generate sidebar styles"""
    is_dark = mode == ThemeMode.DARK

    return f"""
/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--color-surface);
    border-right: 1px solid var(--color-border);
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: var(--spacing-lg);
}}

/* Sidebar navigation */
[data-testid="stSidebar"] .stRadio > div {{
    flex-direction: column;
    gap: var(--spacing-xs);
}}

[data-testid="stSidebar"] .stRadio > div > label {{
    width: 100%;
    justify-content: flex-start;
    border: none;
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
}}

[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
    background-color: {'rgba(76, 175, 80, 0.2)' if is_dark else Colors.PRIMARY_50};
    color: var(--color-primary);
}}
"""


def get_responsive_styles() -> str:
    """Generate responsive styles for mobile devices"""
    return """
/* Mobile responsive adjustments */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: var(--spacing-md);
        padding-right: var(--spacing-md);
    }

    h1 {
        font-size: var(--font-size-2xl);
    }

    h2 {
        font-size: var(--font-size-xl);
    }

    .stRadio > div {
        flex-direction: column;
        gap: var(--spacing-sm);
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 48px;
    }

    div[data-testid="stMetric"] {
        padding: var(--spacing-md);
    }
}

/* Touch-friendly targets */
@media (pointer: coarse) {
    .stButton > button,
    .stDownloadButton > button,
    .stRadio > div > label,
    .stCheckbox > label {
        min-height: 44px;
    }

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox > div > div {
        min-height: 44px;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""


def get_accessibility_styles() -> str:
    """Generate accessibility-focused styles (WCAG 2.1 AA compliance)"""
    return """
/* ============================================
   ACCESSIBILITY CSS - WCAG 2.1 AA Compliance
   ============================================ */

/* Focus visible for keyboard navigation */
*:focus-visible {
    outline: 3px solid var(--color-primary) !important;
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
    outline: 3px solid var(--color-primary) !important;
    outline-offset: 2px !important;
    box-shadow: var(--shadow-focus) !important;
}

/* Input Focus States */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
    outline: 3px solid var(--color-primary) !important;
    outline-offset: 0 !important;
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
}

/* Skip to main content link */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--color-primary);
    color: white;
    padding: var(--spacing-sm) var(--spacing-md);
    z-index: 10000;
    border-radius: 0 0 var(--radius-md) 0;
    transition: top var(--transition-fast);
    text-decoration: none;
    font-weight: 600;
}

.skip-link:focus {
    top: 0;
    outline: 3px solid var(--color-success);
    outline-offset: 2px;
}

/* Screen reader only text */
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

/* Screen reader only - focusable (shows on focus) */
.sr-only-focusable:focus,
.sr-only-focusable:active {
    position: static !important;
    width: auto !important;
    height: auto !important;
    overflow: visible !important;
    clip: auto !important;
    white-space: normal !important;
}

/* Ensure minimum touch target size (44x44px) */
button,
[role="button"],
.stButton > button,
.stCheckbox,
.stRadio label {
    min-height: 44px;
    min-width: 44px;
}

/* Live Region for Announcements */
.live-region,
[aria-live] {
    position: absolute;
    left: -10000px;
    width: 1px;
    height: 1px;
    overflow: hidden;
}

/* Error states with accessible colors */
.error-text {
    color: var(--color-error) !important;
    font-weight: 500;
}

.success-text {
    color: var(--color-success) !important;
    font-weight: 500;
}

.warning-text {
    color: var(--color-warning) !important;
    font-weight: 500;
}

/* Required Field Indicator */
.required-indicator::after {
    content: " *";
    color: var(--color-error);
    font-weight: bold;
}

/* Field Error Styling */
.field-error {
    color: var(--color-error);
    font-size: var(--font-size-sm);
    margin-top: var(--spacing-xs);
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

/* Status Messages */
[role="status"],
[role="alert"] {
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    margin: var(--spacing-sm) 0;
}

[role="alert"] {
    background-color: var(--color-error-light);
    border-left: 4px solid var(--color-error);
}

[role="status"] {
    background-color: var(--color-success-light);
    border-left: 4px solid var(--color-success);
}

/* High contrast mode */
@media (prefers-contrast: high) {
    * {
        border-color: currentColor !important;
    }

    .stButton > button {
        border: 2px solid currentColor !important;
    }

    .stTextInput input,
    .stSelectbox > div > div,
    input,
    textarea,
    select {
        border: 2px solid currentColor !important;
    }

    a {
        text-decoration: underline !important;
    }
}
"""


def get_theme_css(mode: ThemeMode = ThemeMode.DARK) -> str:
    """
    Generate complete theme CSS based on mode.

    Args:
        mode: ThemeMode.DARK or ThemeMode.LIGHT

    Returns:
        Complete CSS string for the theme
    """
    sections = [
        get_google_fonts_import(),
        get_css_variables(mode),
        get_base_styles(mode),
        get_form_styles(mode),
        get_button_styles(mode),
        get_card_styles(mode),
        get_tab_styles(mode),
        get_table_styles(mode),
        get_sidebar_styles(mode),
        get_responsive_styles(),
        get_accessibility_styles(),
    ]

    return "\n".join(sections)


def apply_theme(mode: str = "dark") -> None:
    """
    Apply the design system theme to the Streamlit app.

    Args:
        mode: "dark" or "light"

    Example:
        >>> from design_system import apply_theme
        >>> apply_theme("dark")
    """
    # CSS must be injected every render as Streamlit rebuilds the DOM on each rerun
    theme_mode = ThemeMode.DARK if mode.lower() == "dark" else ThemeMode.LIGHT
    css = get_theme_css(theme_mode)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def get_streamlit_config(mode: str = "dark") -> dict:
    """
    Get Streamlit theme configuration for config.toml

    Args:
        mode: "dark" or "light"

    Returns:
        Dictionary of theme configuration
    """
    if mode.lower() == "dark":
        return {
            "primaryColor": Colors.PRIMARY_500,
            "backgroundColor": Colors.DARK_BG,
            "secondaryBackgroundColor": Colors.DARK_SURFACE,
            "textColor": Colors.DARK_TEXT,
        }
    else:
        return {
            "primaryColor": Colors.PRIMARY_900,
            "backgroundColor": Colors.LIGHT_BG,
            "secondaryBackgroundColor": Colors.LIGHT_SURFACE,
            "textColor": Colors.LIGHT_TEXT,
        }
