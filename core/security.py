"""Security services: password hashing, verification, RBAC decorator helpers, token utilities."""

import functools
import hashlib
import hmac
import secrets
from flask import abort, flash, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(plain_password: str) -> str:
    """Securely hash a plain text password using PBKDF2:SHA256."""
    if not plain_password:
        raise ValueError("Password cannot be empty.")
    return generate_password_hash(plain_password, method="pbkdf2:sha256:600000")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a stored hash."""
    if not plain_password or not hashed_password:
        return False
    return check_password_hash(hashed_password, plain_password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a URL-safe cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_certificate_code(course_id: int, student_id: int, user_uuid: str) -> str:
    """Generate a unique deterministic cryptographic verification code for a certificate."""
    payload = f"LMS-CERT-{course_id}-{student_id}-{user_uuid}"
    raw_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
    return f"LMS-{raw_hash[:4]}-{raw_hash[4:8]}-{raw_hash[8:12]}-{raw_hash[12:16]}"


def login_required(f):
    """Decorator to enforce user login for view functions."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.landing"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """Decorator to enforce role-based access control (Admin, Instructor, Student, etc.)."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                flash("Please log in to access this portal.", "warning")
                return redirect(url_for("auth.landing"))

            user_role = session.get("user_role", "").lower()
            normalized_allowed = [r.lower() for r in allowed_roles]

            if user_role not in normalized_allowed:
                flash("Access denied: You do not have permission for this portal.", "danger")
                # Redirect to appropriate home portal based on actual role
                if user_role == "admin":
                    return redirect(url_for("admin.dashboard"))
                elif user_role == "instructor":
                    return redirect(url_for("instructor.dashboard"))
                elif user_role == "student":
                    return redirect(url_for("student.dashboard"))
                return redirect(url_for("auth.landing"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission_code: str):
    """Decorator to enforce specific granular permission."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.landing"))

            user_permissions = session.get("user_permissions", [])
            user_role = session.get("user_role", "").lower()

            # Superadmin has all permissions
            if user_role == "admin" or permission_code in user_permissions:
                return f(*args, **kwargs)

            flash(f"Permission denied: Missing requirement '{permission_code}'.", "danger")
            return redirect(request.referrer or url_for("auth.landing"))
        return decorated_function
    return decorator
