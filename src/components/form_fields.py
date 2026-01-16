"""
Validated Form Fields

Form field components with built-in validation and formatting.
"""

import streamlit as st
import re
from typing import Tuple, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of field validation"""
    is_valid: bool
    value: Any
    error_message: str = ""


def validate_email(email: str) -> ValidationResult:
    """Validate email format"""
    if not email:
        return ValidationResult(False, email, "Email is required")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return ValidationResult(True, email.lower())
    return ValidationResult(False, email, "Please enter a valid email address")


def validate_phone(phone: str) -> ValidationResult:
    """Validate Nigerian phone number"""
    if not phone:
        return ValidationResult(False, phone, "Phone number is required")

    # Clean the phone number
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')

    # Nigerian phone validation
    if clean.startswith('+234'):
        if len(clean) == 14:
            return ValidationResult(True, clean)
    elif clean.startswith('234'):
        if len(clean) == 13:
            return ValidationResult(True, '+' + clean)
    elif clean.startswith('0'):
        if len(clean) == 11:
            return ValidationResult(True, '+234' + clean[1:])

    return ValidationResult(False, phone, "Please enter a valid Nigerian phone number (e.g., +2348012345678)")


def validate_bvn(bvn: str) -> ValidationResult:
    """Validate BVN (11 digits)"""
    if not bvn:
        return ValidationResult(False, bvn, "BVN is required")

    clean = ''.join(c for c in bvn if c.isdigit())

    if len(clean) == 11:
        return ValidationResult(True, clean)
    return ValidationResult(False, bvn, "BVN must be exactly 11 digits")


def validate_account_number(account: str) -> ValidationResult:
    """Validate NUBAN account number (10 digits)"""
    if not account:
        return ValidationResult(False, account, "Account number is required")

    clean = ''.join(c for c in account if c.isdigit())

    if len(clean) == 10:
        return ValidationResult(True, clean)
    return ValidationResult(False, account, "Account number must be exactly 10 digits")


def validate_required(value: str, field_name: str = "This field") -> ValidationResult:
    """Validate that a field is not empty"""
    if value and value.strip():
        return ValidationResult(True, value.strip())
    return ValidationResult(False, value, f"{field_name} is required")


def validated_text_input(
    label: str,
    key: str,
    placeholder: str = "",
    help_text: str = "",
    required: bool = False,
    validator: Optional[Callable[[str], ValidationResult]] = None,
    show_validation: bool = True,
) -> Tuple[str, bool]:
    """
    Text input with validation feedback.

    Args:
        label: Field label
        key: Streamlit session state key
        placeholder: Placeholder text
        help_text: Help text displayed below
        required: Whether the field is required
        validator: Optional custom validator function
        show_validation: Whether to show validation feedback

    Returns:
        Tuple of (value, is_valid)
    """
    # Get current value
    value = st.text_input(
        label,
        key=key,
        placeholder=placeholder,
        help=help_text,
    )

    is_valid = True
    error_msg = ""

    if show_validation and value:
        if validator:
            result = validator(value)
            is_valid = result.is_valid
            error_msg = result.error_message
        elif required:
            result = validate_required(value, label)
            is_valid = result.is_valid
            error_msg = result.error_message

        if not is_valid and error_msg:
            st.error(error_msg)
        elif is_valid and value:
            st.success("Valid")

    elif required and not value:
        is_valid = False

    return value, is_valid


def validated_email_input(
    label: str = "Email",
    key: str = "email",
    placeholder: str = "example@email.com",
    required: bool = True,
) -> Tuple[str, bool]:
    """
    Email input with validation.

    Returns:
        Tuple of (email, is_valid)
    """
    return validated_text_input(
        label=label,
        key=key,
        placeholder=placeholder,
        validator=validate_email if required else None,
        required=required,
    )


def validated_phone_input(
    label: str = "Phone Number",
    key: str = "phone",
    placeholder: str = "+2348012345678",
    required: bool = True,
) -> Tuple[str, bool]:
    """
    Phone number input with validation.

    Returns:
        Tuple of (phone, is_valid)
    """
    return validated_text_input(
        label=label,
        key=key,
        placeholder=placeholder,
        validator=validate_phone if required else None,
        required=required,
    )


def validated_bvn_input(
    label: str = "BVN",
    key: str = "bvn",
    help_text: str = "Your 11-digit Bank Verification Number",
    required: bool = True,
) -> Tuple[str, bool]:
    """
    BVN input with validation.

    Returns:
        Tuple of (bvn, is_valid)
    """
    return validated_text_input(
        label=label,
        key=key,
        placeholder="12345678901",
        help_text=help_text,
        validator=validate_bvn if required else None,
        required=required,
    )


def validated_number_input(
    label: str,
    key: str,
    min_value: float = 0.0,
    max_value: float = None,
    step: float = 1.0,
    format_str: str = "%.2f",
    help_text: str = "",
    required: bool = False,
) -> Tuple[float, bool]:
    """
    Number input with validation.

    Returns:
        Tuple of (value, is_valid)
    """
    value = st.number_input(
        label,
        key=key,
        min_value=min_value,
        max_value=max_value,
        step=step,
        format=format_str,
        help=help_text,
    )

    is_valid = True
    if required and (value is None or value == 0):
        is_valid = False

    return value, is_valid


def currency_input(
    label: str = "Value of Bonds Applied for",
    key: str = "bond_value",
    min_value: float = 5000.0,
    max_value: float = 50000000.0,
    step: float = 1000.0,
    show_words: bool = True,
) -> Tuple[float, str, bool]:
    """
    Currency input with Naira formatting and amount in words.

    Returns:
        Tuple of (value, amount_in_words, is_valid)
    """
    from utils import format_money_in_words

    value = st.number_input(
        f"{label} (N)",
        key=key,
        min_value=min_value,
        max_value=max_value,
        step=step,
        format="%.2f",
        help=f"Minimum: N{min_value:,.2f}, Maximum: N{max_value:,.2f}",
    )

    # Format display
    formatted = f"N{value:,.2f}"
    st.write(f"**Formatted Value:** {formatted}")

    # Amount in words
    amount_words = ""
    if show_words and value:
        amount_words = format_money_in_words(value)
        st.text_input("Amount in Words", value=amount_words, disabled=True, key=f"{key}_words")

    is_valid = min_value <= value <= max_value

    return value, amount_words, is_valid


def render_field_with_validation(
    field_type: str,
    label: str,
    key: str,
    **kwargs
) -> Tuple[Any, bool]:
    """
    Render a form field with appropriate validation based on type.

    Args:
        field_type: Type of field ('text', 'email', 'phone', 'bvn', 'number', 'currency')
        label: Field label
        key: Session state key
        **kwargs: Additional arguments passed to the field function

    Returns:
        Tuple of (value, is_valid)
    """
    field_map = {
        'text': validated_text_input,
        'email': validated_email_input,
        'phone': validated_phone_input,
        'bvn': validated_bvn_input,
        'number': validated_number_input,
    }

    field_fn = field_map.get(field_type, validated_text_input)
    return field_fn(label=label, key=key, **kwargs)
