"""
PDF Styles

Defines colors, fonts, and table styles matching the official DMO FGNSB form.
"""

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import TableStyle
from reportlab.lib.units import mm


class PDFColors:
    """
    Color palette matching the official DMO form.
    """
    # Primary DMO Green
    DMO_GREEN = HexColor("#006400")
    DMO_GREEN_LIGHT = HexColor("#E8F5E9")
    DMO_GREEN_BORDER = HexColor("#008000")

    # Standard colors
    BLACK = HexColor("#000000")
    WHITE = HexColor("#FFFFFF")
    GRAY = HexColor("#666666")
    LIGHT_GRAY = HexColor("#F5F5F5")
    DARK_GRAY = HexColor("#333333")

    # Form field colors
    FIELD_BORDER = HexColor("#006400")
    FIELD_BG = HexColor("#FFFFFF")
    HEADER_BG = HexColor("#006400")
    HEADER_TEXT = HexColor("#FFFFFF")

    # Status colors
    CHECKED = HexColor("#006400")
    UNCHECKED = HexColor("#FFFFFF")


class PDFStyles:
    """
    PDF styling constants and factory methods for consistent document appearance.
    """

    # Page dimensions
    PAGE_MARGIN = 15 * mm
    SECTION_SPACING = 8 * mm
    FIELD_SPACING = 3 * mm

    # Font settings
    FONT_FAMILY = "Helvetica"
    FONT_FAMILY_BOLD = "Helvetica-Bold"

    # Font sizes
    FONT_SIZE_TITLE = 14
    FONT_SIZE_SUBTITLE = 12
    FONT_SIZE_SECTION_HEADER = 10
    FONT_SIZE_BODY = 9
    FONT_SIZE_SMALL = 8
    FONT_SIZE_TINY = 7

    # Line heights
    LINE_HEIGHT = 14

    # Box dimensions
    CHECKBOX_SIZE = 10
    INPUT_BOX_WIDTH = 14
    INPUT_BOX_HEIGHT = 14

    @classmethod
    def get_title_style(cls) -> ParagraphStyle:
        """Style for main document title"""
        return ParagraphStyle(
            'Title',
            fontName=cls.FONT_FAMILY_BOLD,
            fontSize=cls.FONT_SIZE_TITLE,
            textColor=PDFColors.BLACK,
            alignment=TA_CENTER,
            spaceAfter=6,
            spaceBefore=6,
        )

    @classmethod
    def get_subtitle_style(cls) -> ParagraphStyle:
        """Style for document subtitle"""
        return ParagraphStyle(
            'Subtitle',
            fontName=cls.FONT_FAMILY_BOLD,
            fontSize=cls.FONT_SIZE_SUBTITLE,
            textColor=PDFColors.BLACK,
            alignment=TA_CENTER,
            spaceAfter=4,
        )

    @classmethod
    def get_section_header_style(cls) -> ParagraphStyle:
        """Style for section headers (A, B, C, D labels)"""
        return ParagraphStyle(
            'SectionHeader',
            fontName=cls.FONT_FAMILY_BOLD,
            fontSize=cls.FONT_SIZE_SECTION_HEADER,
            textColor=PDFColors.WHITE,
            alignment=TA_LEFT,
            leftIndent=4,
        )

    @classmethod
    def get_body_style(cls) -> ParagraphStyle:
        """Style for body text"""
        return ParagraphStyle(
            'Body',
            fontName=cls.FONT_FAMILY,
            fontSize=cls.FONT_SIZE_BODY,
            textColor=PDFColors.BLACK,
            alignment=TA_LEFT,
            leading=cls.LINE_HEIGHT,
        )

    @classmethod
    def get_small_style(cls) -> ParagraphStyle:
        """Style for small text like instructions"""
        return ParagraphStyle(
            'Small',
            fontName=cls.FONT_FAMILY,
            fontSize=cls.FONT_SIZE_SMALL,
            textColor=PDFColors.GRAY,
            alignment=TA_LEFT,
            leading=10,
        )

    @classmethod
    def get_label_style(cls) -> ParagraphStyle:
        """Style for field labels"""
        return ParagraphStyle(
            'Label',
            fontName=cls.FONT_FAMILY_BOLD,
            fontSize=cls.FONT_SIZE_BODY,
            textColor=PDFColors.BLACK,
            alignment=TA_LEFT,
        )

    @classmethod
    def get_value_style(cls) -> ParagraphStyle:
        """Style for field values"""
        return ParagraphStyle(
            'Value',
            fontName=cls.FONT_FAMILY,
            fontSize=cls.FONT_SIZE_BODY,
            textColor=PDFColors.BLACK,
            alignment=TA_LEFT,
        )

    @classmethod
    def get_green_header_table_style(cls) -> TableStyle:
        """Table style with green header row matching DMO form"""
        return TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), PDFColors.DMO_GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), PDFColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), cls.FONT_FAMILY_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), cls.FONT_SIZE_SECTION_HEADER),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('LEFTPADDING', (0, 0), (-1, 0), 8),

            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), cls.FONT_FAMILY),
            ('FONTSIZE', (0, 1), (-1, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (0, 1), (-1, -1), PDFColors.BLACK),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('BOX', (0, 0), (-1, -1), 1.5, PDFColors.DMO_GREEN),
        ])

    @classmethod
    def get_form_table_style(cls) -> TableStyle:
        """Standard form table with green borders"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), cls.FONT_FAMILY),
            ('FONTSIZE', (0, 0), (-1, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), PDFColors.BLACK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('BOX', (0, 0), (-1, -1), 1.5, PDFColors.DMO_GREEN),
        ])

    @classmethod
    def get_label_value_table_style(cls) -> TableStyle:
        """Table style for label-value pairs with bold labels"""
        return TableStyle([
            # Label column (first column)
            ('FONTNAME', (0, 0), (0, -1), cls.FONT_FAMILY_BOLD),
            ('FONTSIZE', (0, 0), (0, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (0, 0), (0, -1), PDFColors.BLACK),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.LIGHT_GRAY),

            # Value columns
            ('FONTNAME', (1, 0), (-1, -1), cls.FONT_FAMILY),
            ('FONTSIZE', (1, 0), (-1, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (1, 0), (-1, -1), PDFColors.BLACK),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (1, 0), (-1, -1), 'MIDDLE'),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.DMO_GREEN),
            ('BOX', (0, 0), (-1, -1), 1.5, PDFColors.DMO_GREEN),
        ])

    @classmethod
    def get_borderless_table_style(cls) -> TableStyle:
        """Table style without borders for layout purposes"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), cls.FONT_FAMILY),
            ('FONTSIZE', (0, 0), (-1, -1), cls.FONT_SIZE_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), PDFColors.BLACK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])

    @classmethod
    def get_section_label_style(cls) -> TableStyle:
        """Style for section label cells (A, B, C, D)"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), PDFColors.DMO_GREEN),
            ('TEXTCOLOR', (0, 0), (0, -1), PDFColors.WHITE),
            ('FONTNAME', (0, 0), (0, -1), cls.FONT_FAMILY_BOLD),
            ('FONTSIZE', (0, 0), (0, -1), cls.FONT_SIZE_SECTION_HEADER),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (0, -1), 4),
            ('BOTTOMPADDING', (0, 0), (0, -1), 4),
        ])
