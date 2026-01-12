"""Production-grade logging configuration for Recipier backend."""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure production-grade logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Defaults to INFO in production, DEBUG if RECIPIER_DEBUG env var is set
    """
    import os

    # Determine log level
    if level is None:
        level = "DEBUG" if os.getenv("RECIPIER_DEBUG") else "INFO"

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Production-grade format with timestamp, level, module, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Set log levels for third-party libraries to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup message
    root_logger.info(f"Logging configured at {level.upper()} level")
