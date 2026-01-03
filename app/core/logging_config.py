
"""
Logging Configuration
Sets up structured logging for the application.
"""

import logging
import logging.config
import json
from typing import Optional
from datetime import datetime
import sys


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Allow extra fields via record.extra_data
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """
    Standard text formatter with optional colors for console output.
    """

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        if sys.stdout.isatty():
            levelname = f"{self.COLORS.get(record.levelname, '')}{record.levelname}{self.RESET}"
        else:
            levelname = record.levelname

        base = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{levelname} {record.name}: {record.getMessage()}"
        )

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def setup_logging(
    level: str = "INFO",
    format_type: str = "standard",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        format_type: 'standard' or 'json'.
        log_file: Optional path to log file (if None, logs only to console).

    Returns:
        Configured root application logger.
    """
    logger = logging.getLogger("instagram_automation")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers (avoid duplicates on reload)
    logger.handlers.clear()

    # Choose formatter
    if format_type.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # If file handler fails, log to console only
            logger.error(f"Failed to create file handler: {e}", exc_info=True)

    # Quiet down noisy third‑party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a child logger for a specific module.

    Usage:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(f"instagram_automation.{name}")
