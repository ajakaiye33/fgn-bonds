"""Structured logging configuration using structlog."""

import logging
import sys

import structlog


def configure_logging(json_format: bool = False, log_level: str = "INFO") -> None:
    """
    Configure structlog for the application.

    Args:
        json_format: If True, output JSON logs (for production).
                    If False, use colorful console output (for development).
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Set the log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Shared processors for both environments
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_format:
        # Production: JSON output for log aggregation
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Pretty console output with colors
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with optional name binding.

    Args:
        name: Optional logger name to bind.

    Returns:
        A bound structlog logger.
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(logger_name=name)
    return logger
