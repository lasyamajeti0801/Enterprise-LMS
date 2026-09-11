"""Authentication, session lifecycle, and RBAC tests."""

import pytest
from authentication.services import AuthenticationService
from core.exceptions import AuthenticationError, PermissionDeniedError
from core.security import verify_password
from users.services import UserService


def test_user_creation_and_password_hashing(db_session):
    """Verify password hashing with PBKDF2:SHA256."""
    user = UserService.create_user(
        username="john_doe",
        email="john@example.com",
        password="secretpassword123",
        first_name="John",
        last_name="Doe",
        role_name="student",
    )
    assert user.id is not None
    assert user.password_hash != "secretpassword123"
    assert verify_password("secretpassword123", user.password_hash) is True
    assert verify_password("wrongpassword", user.password_hash) is False


def test_role_boundary_enforcement(db_session, sample_student):
    """Verify that a student account cannot authenticate via the admin portal."""
    student_user, _ = sample_student

    # Authenticating as student via student portal succeeds
    auth_user = AuthenticationService.authenticate_user(
        identifier=student_user.username,
        password="stdpassword123",
        expected_role="student",
    )
    assert auth_user.id == student_user.id

    # Authenticating as student via admin portal must fail with PermissionDeniedError
    with pytest.raises(PermissionDeniedError):
        AuthenticationService.authenticate_user(
            identifier=student_user.username,
            password="stdpassword123",
            expected_role="admin",
        )


def test_account_lockout_on_failed_attempts(db_session, sample_admin):
    """Verify account lockout trigger after 5 consecutive failed passwords."""
    admin = sample_admin
    for _ in range(4):
        with pytest.raises(AuthenticationError):
            AuthenticationService.authenticate_user(
                identifier=admin.username,
                password="wrong_password",
                expected_role="admin",
            )
    assert admin.failed_attempts == 4
    assert admin.is_locked() is False

    # 5th attempt locks the account
    with pytest.raises(AuthenticationError):
        AuthenticationService.authenticate_user(
            identifier=admin.username,
            password="wrong_password",
            expected_role="admin",
        )
    assert admin.is_locked() is True
