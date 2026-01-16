"""
Responsive Design Module

Mobile-first responsive design utilities for the FGN Savings Bond application.
Provides device detection, responsive layouts, and mobile-optimized components.
"""

import streamlit as st
from typing import Optional, Tuple, List
from enum import Enum


class DeviceType(Enum):
    """Device type classification."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class Breakpoint(Enum):
    """CSS breakpoint values."""
    XS = 0       # Extra small (phones)
    SM = 576     # Small (large phones, small tablets)
    MD = 768     # Medium (tablets)
    LG = 992     # Large (desktops)
    XL = 1200    # Extra large (large desktops)
    XXL = 1400   # Extra extra large (wide screens)


def inject_responsive_css():
    """
    Inject responsive CSS for mobile-first design.
    """
    st.markdown("""
    <style>
    /* ============================================
       RESPONSIVE CSS - Mobile First Design
       ============================================ */

    /* Base Mobile Styles (default) */
    :root {
        --container-padding: 12px;
        --card-padding: 16px;
        --section-gap: 24px;
        --font-size-base: 16px;
    }

    /* Container Responsive Padding */
    .main .block-container {
        padding-left: var(--container-padding);
        padding-right: var(--container-padding);
        max-width: 100%;
    }

    /* Mobile-First Typography */
    h1 {
        font-size: clamp(1.5rem, 5vw, 2.5rem);
        line-height: 1.2;
    }

    h2 {
        font-size: clamp(1.25rem, 4vw, 2rem);
        line-height: 1.3;
    }

    h3 {
        font-size: clamp(1.1rem, 3vw, 1.5rem);
        line-height: 1.4;
    }

    /* Responsive Form Elements */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stNumberInput input {
        font-size: 16px !important; /* Prevents iOS zoom */
        padding: 12px !important;
    }

    /* Touch-Friendly Buttons */
    .stButton > button {
        min-height: 48px;
        padding: 12px 24px;
        font-size: 16px;
        touch-action: manipulation;
    }

    /* Responsive Columns - Stack on Mobile */
    @media (max-width: 767px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .row-widget.stHorizontal {
            flex-wrap: wrap;
        }

        /* Full-width inputs on mobile */
        .stTextInput,
        .stTextArea,
        .stSelectbox,
        .stNumberInput,
        .stDateInput {
            width: 100% !important;
        }

        /* Stack radio buttons vertically on mobile */
        .stRadio > div {
            flex-direction: column !important;
        }

        .stRadio label {
            margin-bottom: 8px;
        }

        /* Adjust sidebar for mobile */
        [data-testid="stSidebar"] {
            min-width: 100% !important;
        }

        /* Mobile padding adjustments */
        .main .block-container {
            padding: 1rem !important;
        }

        /* Card-like sections */
        .element-container {
            padding: 8px 0;
        }

        /* Mobile-friendly tables */
        .stDataFrame {
            overflow-x: auto;
        }

        /* Hide less important columns on mobile */
        .hide-on-mobile {
            display: none !important;
        }
    }

    /* Tablet Styles */
    @media (min-width: 768px) and (max-width: 991px) {
        :root {
            --container-padding: 24px;
            --card-padding: 20px;
        }

        .main .block-container {
            max-width: 720px;
            margin: 0 auto;
        }

        /* 2-column layout on tablet */
        [data-testid="column"] {
            min-width: calc(50% - 8px) !important;
        }
    }

    /* Desktop Styles */
    @media (min-width: 992px) {
        :root {
            --container-padding: 32px;
            --card-padding: 24px;
        }

        .main .block-container {
            max-width: 960px;
            margin: 0 auto;
        }
    }

    /* Large Desktop Styles */
    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1140px;
        }
    }

    /* Extra Large Desktop */
    @media (min-width: 1400px) {
        .main .block-container {
            max-width: 1320px;
        }
    }

    /* Touch Device Optimizations */
    @media (hover: none) and (pointer: coarse) {
        /* Increase tap targets */
        button,
        [role="button"],
        a,
        input,
        select,
        textarea {
            min-height: 44px;
        }

        /* Disable hover effects on touch */
        .stButton > button:hover {
            transform: none;
        }

        /* Larger checkboxes and radios */
        input[type="checkbox"],
        input[type="radio"] {
            width: 24px;
            height: 24px;
        }
    }

    /* Responsive Images */
    img {
        max-width: 100%;
        height: auto;
    }

    /* Responsive Metrics Cards */
    [data-testid="metric-container"] {
        min-width: 120px;
        padding: 12px;
    }

    @media (max-width: 767px) {
        [data-testid="metric-container"] {
            text-align: center;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
    }

    /* Responsive Expander */
    .streamlit-expanderHeader {
        padding: 12px 16px;
        font-size: 16px;
    }

    /* Responsive Tabs */
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        font-size: 14px;
    }

    @media (max-width: 767px) {
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 auto;
            text-align: center;
        }
    }

    /* Responsive Progress Indicator */
    .wizard-progress {
        overflow-x: auto;
        padding-bottom: 8px;
    }

    @media (max-width: 767px) {
        .wizard-progress .step-label {
            font-size: 10px;
            max-width: 50px;
        }

        .wizard-progress .step-circle {
            width: 28px;
            height: 28px;
            font-size: 11px;
        }
    }

    /* Safe Area for notched devices */
    @supports (padding: max(0px)) {
        .main .block-container {
            padding-left: max(var(--container-padding), env(safe-area-inset-left));
            padding-right: max(var(--container-padding), env(safe-area-inset-right));
            padding-bottom: max(16px, env(safe-area-inset-bottom));
        }
    }

    /* Print Styles */
    @media print {
        .stSidebar,
        .stButton,
        [data-testid="stSidebar"] {
            display: none !important;
        }

        .main .block-container {
            max-width: 100%;
            padding: 0;
        }

        * {
            color: black !important;
            background: white !important;
        }
    }

    /* Landscape Orientation on Mobile */
    @media (max-width: 896px) and (orientation: landscape) {
        .main .block-container {
            padding-top: 8px;
        }

        h1 {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }
    }

    /* Dark Mode Responsive Adjustments */
    @media (prefers-color-scheme: dark) {
        /* Ensure readability in dark mode */
        .stTextInput input,
        .stTextArea textarea {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
    }

    </style>
    """, unsafe_allow_html=True)


def responsive_columns(
    ratios: List[float],
    mobile_stack: bool = True,
    gap: str = "medium"
) -> List:
    """
    Create responsive columns that stack on mobile.

    Args:
        ratios: List of column width ratios (e.g., [1, 2, 1])
        mobile_stack: Whether to stack columns on mobile
        gap: Gap size ('small', 'medium', 'large')

    Returns:
        List of Streamlit column objects
    """
    gap_sizes = {
        'small': '8px',
        'medium': '16px',
        'large': '24px'
    }

    gap_css = gap_sizes.get(gap, '16px')

    if mobile_stack:
        st.markdown(f"""
        <style>
        .responsive-columns {{
            display: flex;
            gap: {gap_css};
            flex-wrap: wrap;
        }}
        @media (max-width: 767px) {{
            .responsive-columns > div {{
                flex: 1 1 100% !important;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)

    return st.columns(ratios)


def hide_on_mobile(content_key: str):
    """
    Mark content to be hidden on mobile devices.

    Args:
        content_key: Unique key for the content
    """
    st.markdown(f"""
    <style>
    @media (max-width: 767px) {{
        [data-testid="{content_key}"] {{
            display: none !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_only_on_mobile(content_key: str):
    """
    Mark content to only show on mobile devices.

    Args:
        content_key: Unique key for the content
    """
    st.markdown(f"""
    <style>
    @media (min-width: 768px) {{
        [data-testid="{content_key}"] {{
            display: none !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def get_responsive_column_config(
    num_columns: int,
    device: DeviceType = DeviceType.DESKTOP
) -> List[int]:
    """
    Get appropriate column configuration based on device type.

    Args:
        num_columns: Desired number of columns on desktop
        device: Target device type

    Returns:
        List of column ratios
    """
    if device == DeviceType.MOBILE:
        return [1]  # Single column on mobile
    elif device == DeviceType.TABLET:
        return [1] * min(2, num_columns)  # Max 2 columns on tablet
    else:
        return [1] * num_columns


def create_mobile_friendly_form():
    """
    Apply mobile-friendly form styles.
    """
    st.markdown("""
    <style>
    /* Mobile-friendly form adjustments */
    .stForm {
        padding: 16px;
        border-radius: 8px;
    }

    .stForm [data-testid="stFormSubmitButton"] button {
        width: 100%;
        margin-top: 16px;
    }

    @media (max-width: 767px) {
        .stForm {
            padding: 12px;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def create_sticky_header(header_content: str):
    """
    Create a sticky header that stays at top on scroll.

    Args:
        header_content: HTML content for the header
    """
    st.markdown(f"""
    <style>
    .sticky-header {{
        position: sticky;
        top: 0;
        background: var(--background-color, white);
        z-index: 100;
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }}
    </style>
    <div class="sticky-header">
        {header_content}
    </div>
    """, unsafe_allow_html=True)


def create_bottom_navigation(items: List[Tuple[str, str, str]]):
    """
    Create a mobile-friendly bottom navigation bar.

    Args:
        items: List of (label, icon, key) tuples
    """
    nav_items = ""
    for label, icon, key in items:
        nav_items += f"""
        <button class="bottom-nav-item" data-key="{key}">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{label}</span>
        </button>
        """

    st.markdown(f"""
    <style>
    .bottom-nav {{
        display: none;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #ddd;
        padding: 8px;
        padding-bottom: max(8px, env(safe-area-inset-bottom));
        z-index: 1000;
    }}

    @media (max-width: 767px) {{
        .bottom-nav {{
            display: flex;
            justify-content: space-around;
        }}

        /* Add padding to main content to account for bottom nav */
        .main .block-container {{
            padding-bottom: 80px !important;
        }}
    }}

    .bottom-nav-item {{
        display: flex;
        flex-direction: column;
        align-items: center;
        background: none;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        color: #666;
        font-size: 12px;
    }}

    .bottom-nav-item:hover,
    .bottom-nav-item.active {{
        color: #006400;
    }}

    .nav-icon {{
        font-size: 20px;
        margin-bottom: 4px;
    }}
    </style>
    <nav class="bottom-nav" role="navigation" aria-label="Main navigation">
        {nav_items}
    </nav>
    """, unsafe_allow_html=True)


def setup_responsive():
    """
    Set up all responsive features for the application.
    Call this at the start of your Streamlit app.
    """
    # CSS must be injected every render as Streamlit rebuilds the DOM on each rerun
    inject_responsive_css()
    create_mobile_friendly_form()
