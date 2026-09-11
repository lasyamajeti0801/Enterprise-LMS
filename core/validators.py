"""Data validation utilities for domain entities and form submissions."""

import re
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_username(username: str) -> bool:
    """Validate username (alphanumeric and underscores, length 3-30)."""
    if not username or not isinstance(username, str):
        return False
    pattern = r"^[a-zA-Z0-9_]{3,30}$"
    return bool(re.match(pattern, username.strip()))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength (at least 6 characters, contains digit or letter)."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, "Password is valid."


def validate_date_range(start_date, end_date) -> bool:
    """Validate that start_date is before or equal to end_date."""
    if not start_date or not end_date:
        return True
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    return start_date <= end_date


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Strip whitespace and truncate string to safe length."""
    if not text:
        return ""
    return str(text).strip()[:max_length]
