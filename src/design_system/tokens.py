"""
Design Tokens

Central source of truth for all design values used throughout the application.
Based on DMO Nigeria's official branding guidelines.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Colors:
    """
    Color palette following DMO Nigeria branding.
    Primary: Official DMO green
    """
    # Primary DMO Green palette
    PRIMARY_50 = "#E8F5E9"
    PRIMARY_100 = "#C8E6C9"
    PRIMARY_200 = "#A5D6A7"
    PRIMARY_300 = "#81C784"
    PRIMARY_400 = "#66BB6A"
    PRIMARY_500 = "#4CAF50"
    PRIMARY_600 = "#43A047"
    PRIMARY_700 = "#388E3C"
    PRIMARY_800 = "#2E7D32"
    PRIMARY_900 = "#006400"  # Official DMO dark green

    # Neutral palette
    NEUTRAL_50 = "#FAFAFA"
    NEUTRAL_100 = "#F5F5F5"
    NEUTRAL_200 = "#EEEEEE"
    NEUTRAL_300 = "#E0E0E0"
    NEUTRAL_400 = "#BDBDBD"
    NEUTRAL_500 = "#9E9E9E"
    NEUTRAL_600 = "#757575"
    NEUTRAL_700 = "#616161"
    NEUTRAL_800 = "#424242"
    NEUTRAL_900 = "#212121"

    # Dark theme specific
    DARK_BG = "#0D1117"
    DARK_SURFACE = "#161B22"
    DARK_ELEVATED = "#21262D"
    DARK_BORDER = "#30363D"
    DARK_TEXT = "#E6EDF3"
    DARK_TEXT_SECONDARY = "#8B949E"

    # Light theme specific
    LIGHT_BG = "#FFFFFF"
    LIGHT_SURFACE = "#F6F8FA"
    LIGHT_ELEVATED = "#FFFFFF"
    LIGHT_BORDER = "#D0D7DE"
    LIGHT_TEXT = "#1F2328"
    LIGHT_TEXT_SECONDARY = "#656D76"

    # Semantic colors
    SUCCESS = "#2DA44E"
    SUCCESS_LIGHT = "#DAFBE1"
    ERROR = "#CF222E"
    ERROR_LIGHT = "#FFEBE9"
    WARNING = "#BF8700"
    WARNING_LIGHT = "#FFF8C5"
    INFO = "#0969DA"
    INFO_LIGHT = "#DDF4FF"

    # Dark theme semantic backgrounds (semi-transparent for dark mode)
    SUCCESS_DARK = "rgba(45, 164, 78, 0.15)"
    ERROR_DARK = "rgba(207, 34, 46, 0.15)"
    WARNING_DARK = "rgba(191, 135, 0, 0.15)"
    INFO_DARK = "rgba(9, 105, 218, 0.15)"

    # Special
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    TRANSPARENT = "transparent"

    @classmethod
    def get_dark_palette(cls) -> Dict[str, str]:
        """Get color values for dark theme"""
        return {
            'bg': cls.DARK_BG,
            'surface': cls.DARK_SURFACE,
            'elevated': cls.DARK_ELEVATED,
            'border': cls.DARK_BORDER,
            'text': cls.DARK_TEXT,
            'text_secondary': cls.DARK_TEXT_SECONDARY,
            'primary': cls.PRIMARY_500,
            'primary_hover': cls.PRIMARY_400,
            'primary_dark': cls.PRIMARY_900,
        }

    @classmethod
    def get_light_palette(cls) -> Dict[str, str]:
        """Get color values for light theme"""
        return {
            'bg': cls.LIGHT_BG,
            'surface': cls.LIGHT_SURFACE,
            'elevated': cls.LIGHT_ELEVATED,
            'border': cls.LIGHT_BORDER,
            'text': cls.LIGHT_TEXT,
            'text_secondary': cls.LIGHT_TEXT_SECONDARY,
            'primary': cls.PRIMARY_900,
            'primary_hover': cls.PRIMARY_700,
            'primary_dark': cls.PRIMARY_900,
        }


@dataclass(frozen=True)
class Typography:
    """
    Typography scale and font settings.
    Uses Poppins as primary font with Inter as fallback.
    """
    # Font family
    FONT_FAMILY = "'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', Consolas, monospace"

    # Font sizes (using rem for accessibility)
    SIZE_XS = "0.75rem"     # 12px
    SIZE_SM = "0.875rem"    # 14px
    SIZE_BASE = "1rem"      # 16px
    SIZE_LG = "1.125rem"    # 18px
    SIZE_XL = "1.25rem"     # 20px
    SIZE_2XL = "1.5rem"     # 24px
    SIZE_3XL = "1.875rem"   # 30px
    SIZE_4XL = "2.25rem"    # 36px
    SIZE_5XL = "3rem"       # 48px

    # Font weights
    WEIGHT_LIGHT = "300"
    WEIGHT_REGULAR = "400"
    WEIGHT_MEDIUM = "500"
    WEIGHT_SEMIBOLD = "600"
    WEIGHT_BOLD = "700"

    # Line heights
    LINE_HEIGHT_TIGHT = "1.25"
    LINE_HEIGHT_NORMAL = "1.5"
    LINE_HEIGHT_RELAXED = "1.75"

    # Letter spacing
    LETTER_SPACING_TIGHT = "-0.025em"
    LETTER_SPACING_NORMAL = "0"
    LETTER_SPACING_WIDE = "0.025em"


@dataclass(frozen=True)
class Spacing:
    """
    Spacing scale based on 4px base unit.
    Provides consistent spacing throughout the application.
    """
    NONE = "0"
    PX = "1px"
    XS = "0.25rem"    # 4px
    SM = "0.5rem"     # 8px
    MD = "1rem"       # 16px
    LG = "1.5rem"     # 24px
    XL = "2rem"       # 32px
    XXL = "3rem"      # 48px
    XXXL = "4rem"     # 64px

    # Specific use cases
    FORM_GAP = "1rem"
    SECTION_GAP = "2rem"
    CARD_PADDING = "1.5rem"
    INPUT_PADDING_X = "0.75rem"
    INPUT_PADDING_Y = "0.625rem"
    BUTTON_PADDING_X = "1.25rem"
    BUTTON_PADDING_Y = "0.625rem"


@dataclass(frozen=True)
class Shadows:
    """
    Shadow definitions for elevation hierarchy.
    """
    NONE = "none"
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    BASE = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"
    XXL = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"

    # Colored shadows for focus states
    FOCUS_PRIMARY = "0 0 0 3px rgba(76, 175, 80, 0.4)"
    FOCUS_ERROR = "0 0 0 3px rgba(207, 34, 46, 0.4)"

    # Dark theme shadows
    DARK_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.3)"
    DARK_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)"
    DARK_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.4)"


@dataclass(frozen=True)
class BorderRadius:
    """
    Border radius scale for consistent roundedness.
    """
    NONE = "0"
    SM = "0.25rem"    # 4px
    BASE = "0.375rem" # 6px
    MD = "0.5rem"     # 8px
    LG = "0.75rem"    # 12px
    XL = "1rem"       # 16px
    XXL = "1.5rem"    # 24px
    FULL = "9999px"


@dataclass(frozen=True)
class Transitions:
    """
    Transition timing functions and durations.
    """
    DURATION_FAST = "150ms"
    DURATION_BASE = "200ms"
    DURATION_SLOW = "300ms"
    DURATION_SLOWER = "500ms"

    EASE_DEFAULT = "cubic-bezier(0.4, 0, 0.2, 1)"
    EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
    EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
    EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"

    # Common transitions
    ALL = f"all {DURATION_BASE} {EASE_DEFAULT}"
    COLORS = f"color {DURATION_FAST} {EASE_DEFAULT}, background-color {DURATION_FAST} {EASE_DEFAULT}, border-color {DURATION_FAST} {EASE_DEFAULT}"
    TRANSFORM = f"transform {DURATION_BASE} {EASE_DEFAULT}"
    OPACITY = f"opacity {DURATION_BASE} {EASE_DEFAULT}"


@dataclass(frozen=True)
class Breakpoints:
    """
    Responsive breakpoints for media queries.
    """
    SM = "640px"
    MD = "768px"
    LG = "1024px"
    XL = "1280px"
    XXL = "1536px"


@dataclass(frozen=True)
class ZIndex:
    """
    Z-index scale for layering.
    """
    DROPDOWN = "1000"
    STICKY = "1020"
    FIXED = "1030"
    MODAL_BACKDROP = "1040"
    MODAL = "1050"
    POPOVER = "1060"
    TOOLTIP = "1070"
    TOAST = "1080"
