"""
PDF Custom Elements

Custom drawing elements for the DMO form including checkboxes, input boxes,
signature lines, and stamp areas.
"""

from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Table, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .styles import PDFColors, PDFStyles
from typing import Optional, List


class CheckboxField(Flowable):
    """
    A checkbox element that can be checked or unchecked.
    Matches the DMO form checkbox styling with green borders.
    """

    def __init__(self, label: str, checked: bool = False,
                 size: float = 10, label_width: float = 80):
        Flowable.__init__(self)
        self.label = label
        self.checked = checked
        self.size = size
        self.label_width = label_width
        self.width = size + label_width + 5
        self.height = max(size, 12)

    def draw(self):
        canvas = self.canv

        # Draw checkbox box
        canvas.setStrokeColor(PDFColors.DMO_GREEN)
        canvas.setLineWidth(1)
        canvas.rect(0, (self.height - self.size) / 2, self.size, self.size)

        # Draw checkmark if checked
        if self.checked:
            canvas.setFillColor(PDFColors.DMO_GREEN)
            canvas.setFont(PDFStyles.FONT_FAMILY_BOLD, self.size - 2)
            # Draw a checkmark character
            canvas.drawString(1.5, (self.height - self.size) / 2 + 1.5, "X")

        # Draw label
        canvas.setFillColor(PDFColors.BLACK)
        canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_BODY)
        canvas.drawString(self.size + 4, (self.height - PDFStyles.FONT_SIZE_BODY) / 2, self.label)


class CheckboxGroup(Flowable):
    """
    A group of checkboxes arranged horizontally.
    """

    def __init__(self, options: List[tuple], selected: Optional[str] = None,
                 spacing: float = 20, checkbox_size: float = 10):
        """
        Args:
            options: List of (value, label) tuples
            selected: The selected value (only one can be selected)
            spacing: Space between checkboxes
            checkbox_size: Size of checkbox squares
        """
        Flowable.__init__(self)
        self.options = options
        self.selected = selected
        self.spacing = spacing
        self.checkbox_size = checkbox_size

        # Calculate total width
        self.width = sum(checkbox_size + len(label) * 5 + spacing for _, label in options)
        self.height = max(checkbox_size, 14)

    def draw(self):
        canvas = self.canv
        x_offset = 0

        for value, label in self.options:
            is_checked = (value == self.selected)

            # Draw checkbox
            canvas.setStrokeColor(PDFColors.DMO_GREEN)
            canvas.setLineWidth(1)
            y = (self.height - self.checkbox_size) / 2
            canvas.rect(x_offset, y, self.checkbox_size, self.checkbox_size)

            # Draw checkmark if selected
            if is_checked:
                canvas.setFillColor(PDFColors.DMO_GREEN)
                canvas.setFont(PDFStyles.FONT_FAMILY_BOLD, self.checkbox_size - 2)
                canvas.drawString(x_offset + 2, y + 2, "X")

            # Draw label
            canvas.setFillColor(PDFColors.BLACK)
            canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_BODY)
            label_x = x_offset + self.checkbox_size + 3
            canvas.drawString(label_x, y + 1, label)

            # Move to next checkbox position
            x_offset += self.checkbox_size + len(label) * 5 + self.spacing


class InputBoxes(Flowable):
    """
    Individual character input boxes like those used for CSCS, CHN, BVN, etc.
    Each character gets its own box.
    """

    def __init__(self, value: str = "", num_boxes: int = 12,
                 box_width: float = 12, box_height: float = 14,
                 prefix: str = ""):
        Flowable.__init__(self)
        self.value = str(value).upper() if value else ""
        self.num_boxes = num_boxes
        self.box_width = box_width
        self.box_height = box_height
        self.prefix = prefix
        self.width = (num_boxes * box_width) + (len(prefix) * 6 if prefix else 0)
        self.height = box_height

    def draw(self):
        canvas = self.canv
        x_offset = 0

        # Draw prefix if provided
        if self.prefix:
            canvas.setFillColor(PDFColors.BLACK)
            canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_SMALL)
            canvas.drawString(0, (self.box_height - PDFStyles.FONT_SIZE_SMALL) / 2, self.prefix)
            x_offset = len(self.prefix) * 5 + 4

        # Draw boxes
        canvas.setStrokeColor(PDFColors.DMO_GREEN)
        canvas.setLineWidth(0.75)

        for i in range(self.num_boxes):
            box_x = x_offset + (i * self.box_width)

            # Draw box
            canvas.rect(box_x, 0, self.box_width, self.box_height)

            # Draw character if available
            if i < len(self.value):
                canvas.setFillColor(PDFColors.BLACK)
                canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_BODY)
                # Center the character in the box
                char_x = box_x + (self.box_width - 5) / 2
                char_y = (self.box_height - PDFStyles.FONT_SIZE_BODY) / 2
                canvas.drawString(char_x, char_y, self.value[i])


class PhoneInputBoxes(InputBoxes):
    """
    Specialized input boxes for phone numbers with country code indicator.
    """

    def __init__(self, value: str = "", prefix: str = ""):
        # Clean the phone number
        clean_value = ''.join(c for c in str(value) if c.isdigit() or c == '+')
        super().__init__(value=clean_value, num_boxes=14, box_width=11, prefix=prefix)


class SignatureLine(Flowable):
    """
    A signature line with label.
    """

    def __init__(self, label: str, width: float = 150, include_date: bool = True):
        Flowable.__init__(self)
        self.label = label
        self.line_width = width
        self.include_date = include_date
        self.width = width + (80 if include_date else 0)
        self.height = 30

    def draw(self):
        canvas = self.canv

        # Draw signature line
        canvas.setStrokeColor(PDFColors.BLACK)
        canvas.setLineWidth(0.5)
        canvas.line(0, 15, self.line_width, 15)

        # Draw label
        canvas.setFillColor(PDFColors.BLACK)
        canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_SMALL)
        canvas.drawString(0, 3, self.label)

        # Draw date line if included
        if self.include_date:
            date_x = self.line_width + 20
            canvas.line(date_x, 15, date_x + 60, 15)
            canvas.drawString(date_x, 3, "Date:")


class StampArea(Flowable):
    """
    A bordered area for stamps or seals.
    """

    def __init__(self, label: str = "Stamp of Receiving Agent",
                 width: float = 100, height: float = 60):
        Flowable.__init__(self)
        self.label = label
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv

        # Draw border
        canvas.setStrokeColor(PDFColors.DMO_GREEN)
        canvas.setLineWidth(1)
        canvas.rect(0, 10, self.width, self.height - 10)

        # Draw label
        canvas.setFillColor(PDFColors.BLACK)
        canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_SMALL)
        # Center the label below the box
        label_width = canvas.stringWidth(self.label, PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_SMALL)
        canvas.drawString((self.width - label_width) / 2, 0, self.label)


class SectionHeader(Flowable):
    """
    A section header with green background and white text.
    Includes the section letter (A, B, C, D) in a separate cell.
    """

    def __init__(self, letter: str, title: str, width: float = 500):
        Flowable.__init__(self)
        self.letter = letter
        self.title = title
        self.width = width
        self.height = 20
        self.letter_width = 20

    def draw(self):
        canvas = self.canv

        # Draw letter cell background
        canvas.setFillColor(PDFColors.DMO_GREEN)
        canvas.rect(0, 0, self.letter_width, self.height, fill=1, stroke=0)

        # Draw letter
        canvas.setFillColor(PDFColors.WHITE)
        canvas.setFont(PDFStyles.FONT_FAMILY_BOLD, PDFStyles.FONT_SIZE_SECTION_HEADER)
        letter_x = (self.letter_width - canvas.stringWidth(self.letter, PDFStyles.FONT_FAMILY_BOLD,
                                                          PDFStyles.FONT_SIZE_SECTION_HEADER)) / 2
        canvas.drawString(letter_x, 5, self.letter)

        # Draw title background
        canvas.setFillColor(PDFColors.DMO_GREEN_LIGHT)
        canvas.rect(self.letter_width, 0, self.width - self.letter_width, self.height, fill=1, stroke=0)

        # Draw title
        canvas.setFillColor(PDFColors.BLACK)
        canvas.setFont(PDFStyles.FONT_FAMILY_BOLD, PDFStyles.FONT_SIZE_SECTION_HEADER)
        canvas.drawString(self.letter_width + 8, 5, self.title)

        # Draw border
        canvas.setStrokeColor(PDFColors.DMO_GREEN)
        canvas.setLineWidth(1)
        canvas.rect(0, 0, self.width, self.height, fill=0, stroke=1)


class ThumbprintArea(Flowable):
    """
    Area for thumbprint with label.
    """

    def __init__(self, width: float = 80, height: float = 60):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv

        # Draw border
        canvas.setStrokeColor(PDFColors.DMO_GREEN)
        canvas.setLineWidth(1)
        canvas.rect(0, 15, self.width, self.height - 15)

        # Draw section letter
        canvas.setFillColor(PDFColors.DMO_GREEN)
        canvas.setFont(PDFStyles.FONT_FAMILY_BOLD, PDFStyles.FONT_SIZE_SECTION_HEADER)
        canvas.drawString(5, self.height - 12, "C")

        # Draw label
        canvas.setFillColor(PDFColors.BLACK)
        canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_SMALL)
        canvas.drawString(0, 3, "Thumb print of")
        canvas.drawString(0, -6, "illiterate applicant")


class DottedInputLine(Flowable):
    """
    A dotted line for handwritten input with optional value displayed.
    """

    def __init__(self, label: str = "", value: str = "", width: float = 200,
                 label_width: float = 100):
        Flowable.__init__(self)
        self.label = label
        self.value = value
        self.line_width = width
        self.label_width = label_width
        self.width = label_width + width
        self.height = 16

    def draw(self):
        canvas = self.canv

        # Draw label
        if self.label:
            canvas.setFillColor(PDFColors.BLACK)
            canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_BODY)
            canvas.drawString(0, 4, self.label)

        # Draw dotted line
        canvas.setStrokeColor(PDFColors.GRAY)
        canvas.setLineWidth(0.5)
        canvas.setDash(2, 2)
        line_start = self.label_width if self.label else 0
        canvas.line(line_start, 2, line_start + self.line_width, 2)
        canvas.setDash()  # Reset dash

        # Draw value if provided
        if self.value:
            canvas.setFillColor(PDFColors.BLACK)
            canvas.setFont(PDFStyles.FONT_FAMILY, PDFStyles.FONT_SIZE_BODY)
            canvas.drawString(line_start + 5, 4, str(self.value))
