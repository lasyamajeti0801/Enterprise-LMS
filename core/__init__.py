"""Core engine and foundation utilities for Enterprise LMS."""

from core.database import Base, ModelMixin, close_session, get_session, get_utc_now, init_db
from core.events import events
from core.exceptions import (
    AssessmentError,
    AuthenticationError,
    CertificateIneligibleError,
    CourseNotFoundError,
    EnrollmentError,
    LMSException,
    PermissionDeniedError,
    ResourceNotFoundError,
    ValidationError,
)
from core.pagination import Page, paginate_query
from core.security import (
    generate_certificate_code,
    generate_secure_token,
    hash_password,
    login_required,
    permission_required,
    role_required,
    verify_password,
)

__all__ = [
    "Base",
    "ModelMixin",
    "init_db",
    "get_session",
    "close_session",
    "get_utc_now",
    "events",
    "LMSException",
    "AuthenticationError",
    "PermissionDeniedError",
    "ResourceNotFoundError",
    "ValidationError",
    "CourseNotFoundError",
    "EnrollmentError",
    "AssessmentError",
    "CertificateIneligibleError",
    "Page",
    "paginate_query",
    "hash_password",
    "verify_password",
    "generate_secure_token",
    "generate_certificate_code",
    "login_required",
    "role_required",
    "permission_required",
]
