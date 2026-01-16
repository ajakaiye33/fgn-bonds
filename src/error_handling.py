"""
Error Handling Module

Graceful error handling and user-friendly error messages for the FGN Savings Bond application.
"""

import streamlit as st
import logging
import traceback
from typing import Optional, Callable, Any, Dict
from functools import wraps
from datetime import datetime
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fgn_bonds')


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(Enum):
    """Standard error codes for the application."""
    # Database errors (1xxx)
    DB_CONNECTION_FAILED = 1001
    DB_QUERY_FAILED = 1002
    DB_SAVE_FAILED = 1003
    DB_NOT_FOUND = 1004

    # Validation errors (2xxx)
    VALIDATION_FAILED = 2001
    INVALID_INPUT = 2002
    MISSING_REQUIRED_FIELD = 2003
    INVALID_FORMAT = 2004

    # PDF errors (3xxx)
    PDF_GENERATION_FAILED = 3001
    PDF_TEMPLATE_ERROR = 3002

    # Authentication errors (4xxx)
    AUTH_FAILED = 4001
    SESSION_EXPIRED = 4002
    UNAUTHORIZED = 4003

    # General errors (5xxx)
    UNKNOWN_ERROR = 5001
    NETWORK_ERROR = 5002
    TIMEOUT_ERROR = 5003


# User-friendly error messages
ERROR_MESSAGES = {
    ErrorCode.DB_CONNECTION_FAILED: {
        "title": "Database Connection Error",
        "message": "We couldn't connect to the database. Your data will be saved locally.",
        "action": "Please try again later or contact support if the issue persists.",
        "severity": ErrorSeverity.WARNING,
    },
    ErrorCode.DB_QUERY_FAILED: {
        "title": "Data Retrieval Error",
        "message": "We couldn't retrieve the requested data.",
        "action": "Please refresh the page and try again.",
        "severity": ErrorSeverity.ERROR,
    },
    ErrorCode.DB_SAVE_FAILED: {
        "title": "Save Error",
        "message": "We couldn't save your application.",
        "action": "Please check your information and try again.",
        "severity": ErrorSeverity.ERROR,
    },
    ErrorCode.VALIDATION_FAILED: {
        "title": "Validation Error",
        "message": "Some of the information you provided is invalid.",
        "action": "Please review the highlighted fields and correct any errors.",
        "severity": ErrorSeverity.WARNING,
    },
    ErrorCode.PDF_GENERATION_FAILED: {
        "title": "PDF Generation Error",
        "message": "We couldn't generate your application PDF.",
        "action": "Your application has been saved. You can download the PDF later.",
        "severity": ErrorSeverity.WARNING,
    },
    ErrorCode.AUTH_FAILED: {
        "title": "Authentication Failed",
        "message": "Invalid username or password.",
        "action": "Please check your credentials and try again.",
        "severity": ErrorSeverity.ERROR,
    },
    ErrorCode.UNKNOWN_ERROR: {
        "title": "Unexpected Error",
        "message": "An unexpected error occurred.",
        "action": "Please try again. If the problem persists, contact support.",
        "severity": ErrorSeverity.ERROR,
    },
}


def get_error_info(error_code: ErrorCode) -> Dict[str, Any]:
    """
    Get user-friendly error information for an error code.

    Args:
        error_code: The error code

    Returns:
        Dictionary with error information
    """
    return ERROR_MESSAGES.get(error_code, ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR])


def display_error(
    error_code: ErrorCode,
    details: Optional[str] = None,
    show_details: bool = False
):
    """
    Display a user-friendly error message.

    Args:
        error_code: The error code
        details: Technical details (for debugging)
        show_details: Whether to show technical details
    """
    error_info = get_error_info(error_code)
    severity = error_info["severity"]

    # Choose the appropriate Streamlit function
    if severity == ErrorSeverity.INFO:
        display_fn = st.info
    elif severity == ErrorSeverity.WARNING:
        display_fn = st.warning
    elif severity == ErrorSeverity.CRITICAL:
        display_fn = st.error
    else:
        display_fn = st.error

    # Display main error message
    display_fn(f"""
    **{error_info['title']}**

    {error_info['message']}

    *{error_info['action']}*
    """)

    # Show technical details if requested
    if show_details and details:
        with st.expander("Technical Details"):
            st.code(details)

    # Log the error
    logger.error(
        f"Error {error_code.value}: {error_info['title']} - {details or 'No details'}"
    )


def display_validation_errors(errors: list):
    """
    Display validation errors in a user-friendly format.

    Args:
        errors: List of validation error messages
    """
    if not errors:
        return

    st.error("**Please fix the following issues:**")

    for error in errors:
        st.markdown(f"- {error}")

    st.info("*Please correct these errors and try again.*")


def display_success(
    title: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Display a success message with optional details.

    Args:
        title: Success message title
        message: Success message body
        details: Optional details to display
    """
    st.success(f"""
    **{title}**

    {message}
    """)

    if details:
        with st.expander("Details"):
            for key, value in details.items():
                st.write(f"**{key}:** {value}")


def safe_execute(
    func: Callable,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    default_return: Any = None,
    show_error: bool = True
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        error_code: Error code to use if function fails
        default_return: Value to return on error
        show_error: Whether to display error to user

    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        error_details = f"{str(e)}\n\n{traceback.format_exc()}"
        logger.error(f"Error in safe_execute: {error_details}")

        if show_error:
            display_error(error_code, error_details, show_details=False)

        return default_return


def error_handler(
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    default_return: Any = None,
    log_errors: bool = True
):
    """
    Decorator for error handling on functions.

    Args:
        error_code: Error code to use on failure
        default_return: Value to return on error
        log_errors: Whether to log errors

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_details = f"{str(e)}\n\n{traceback.format_exc()}"

                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {error_details}"
                    )

                display_error(error_code, error_details)
                return default_return

        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR
):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries
        error_code: Error code to use if all retries fail

    Returns:
        Decorated function
    """
    import time

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds)

            # All retries failed
            error_details = f"All {max_attempts} attempts failed. Last error: {last_error}"
            display_error(error_code, error_details)
            return None

        return wrapper
    return decorator


def create_error_boundary(component_name: str):
    """
    Create an error boundary context manager for a component.

    Args:
        component_name: Name of the component (for logging)

    Returns:
        Context manager
    """
    class ErrorBoundary:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                logger.error(
                    f"Error in {component_name}: {exc_val}\n{traceback.format_exc()}"
                )
                st.error(f"""
                **Component Error**

                The {component_name} encountered an error and couldn't be displayed.

                *Please refresh the page or contact support if this persists.*
                """)
                return True  # Suppress the exception
            return False

    return ErrorBoundary()


def log_user_action(action: str, details: Optional[Dict[str, Any]] = None):
    """
    Log a user action for auditing purposes.

    Args:
        action: Description of the action
        details: Additional details
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {},
    }
    logger.info(f"User Action: {log_entry}")


def handle_database_error(func: Callable) -> Callable:
    """
    Decorator specifically for database operations.

    Args:
        func: Database function to wrap

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            display_error(ErrorCode.DB_CONNECTION_FAILED)
            return None
        except TimeoutError:
            display_error(ErrorCode.TIMEOUT_ERROR)
            return None
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            display_error(ErrorCode.DB_QUERY_FAILED, str(e))
            return None

    return wrapper


def show_loading_with_error_handling(
    message: str,
    func: Callable,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR
) -> Any:
    """
    Show a loading spinner while executing a function with error handling.

    Args:
        message: Loading message to display
        func: Function to execute
        error_code: Error code to use on failure

    Returns:
        Function result or None on error
    """
    try:
        with st.spinner(message):
            return func()
    except Exception as e:
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        display_error(error_code, error_details)
        return None


def setup_error_handling():
    """
    Set up global error handling for the application.
    Call this at the start of your Streamlit app.
    """
    # Set up uncaught exception handler (only once per session)
    import sys

    if '_error_handling_initialized' not in st.session_state:
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

        sys.excepthook = handle_exception
        st.session_state._error_handling_initialized = True

    # CSS must be injected every render as Streamlit rebuilds the DOM on each rerun
    st.markdown("""
    <style>
    /* Error message styling - complements theme.py */
    [data-testid="stAlert"],
    .stAlert {
        border-radius: 8px !important;
        padding: 16px !important;
    }

    [data-testid="stAlert"] p,
    .stAlert p {
        margin: 8px 0 !important;
    }

    [data-testid="stAlert"] strong,
    .stAlert strong {
        font-size: 1.1em !important;
    }

    [data-testid="stAlert"] em,
    .stAlert em {
        font-size: 0.9em !important;
        opacity: 0.8 !important;
    }

    /* Ensure alert text is visible in dark mode */
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: var(--color-text, #E6EDF3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
