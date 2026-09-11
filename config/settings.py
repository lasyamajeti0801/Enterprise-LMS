"""Enterprise Learning Management System - Configuration Module.

Provides comprehensive settings for Development, Testing, and Production environments
with full support for local SQLite and production PostgreSQL, session security,
asset directories, and feature flags.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration settings shared across all environments."""

    SECRET_KEY = os.environ.get("LMS_SECRET_KEY", "enterprise-lms-secure-key-2026-production-ready")
    APP_NAME = "Enterprise LMS"
    APP_VERSION = "2.5.0"
    APP_TIMEZONE = "UTC"

    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DATABASE_CONNECT_TIMEOUT = 30

    # Session settings
    SESSION_COOKIE_NAME = "lms_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Upload & Storage Directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    CERTIFICATES_FOLDER = os.path.join(UPLOAD_FOLDER, "certificates")
    EXPORTS_FOLDER = os.path.join(UPLOAD_FOLDER, "exports")
    AVATARS_FOLDER = os.path.join(UPLOAD_FOLDER, "avatars")
    SUBMISSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, "submissions")
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max payload

    # Assessment & Grading Defaults
    DEFAULT_PASSING_PERCENTAGE = 60.0
    DEFAULT_MAX_QUIZ_ATTEMPTS = 3
    DEFAULT_QUIZ_DURATION_MINUTES = 30
    DEFAULT_ATTENDANCE_MINIMUM_PERCENTAGE = 75.0

    # Gamification Defaults
    XP_LESSON_COMPLETED = 50
    XP_QUIZ_PASSED = 100
    XP_ASSIGNMENT_SUBMITTED = 80
    XP_COURSE_COMPLETED = 500
    XP_DAILY_STREAK_BONUS = 25

    # Pagination Defaults
    ITEMS_PER_PAGE = 15
    MAX_ITEMS_PER_PAGE = 100

    # Security
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    # Local Email/Notification Retention
    NOTIFICATION_RETENTION_DAYS = 90

    @classmethod
    def ensure_directories(cls):
        """Ensure all required runtime directories exist."""
        for folder in [
            cls.UPLOAD_FOLDER,
            cls.CERTIFICATES_FOLDER,
            cls.EXPORTS_FOLDER,
            cls.AVATARS_FOLDER,
            cls.SUBMISSIONS_FOLDER,
        ]:
            os.makedirs(folder, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'lms_dev.db')}"
    )


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'lms_prod.db')}"
    )


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name=None):
    """Retrieve configuration class by environment name."""
    if env_name is None:
        env_name = os.environ.get("FLASK_ENV", "development").lower()
    return CONFIG_MAP.get(env_name, DevelopmentConfig)
