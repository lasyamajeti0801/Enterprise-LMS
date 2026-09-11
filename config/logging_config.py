"""Structured enterprise logging setup for the LMS application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app=None, log_level=logging.INFO):
    """Configure comprehensive structured logging to console and rotating log file."""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "lms_system.log")

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Rotating file handler (5 MB per file, up to 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if already added
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    if app is not None:
        app.logger.setLevel(log_level)
        if not app.logger.handlers:
            app.logger.addHandler(console_handler)
            app.logger.addHandler(file_handler)

    logging.info("Enterprise LMS logging initialized successfully.")
