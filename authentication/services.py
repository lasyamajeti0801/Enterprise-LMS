"""Authentication services supporting role-specific logins, lockout protection, and history tracking."""

from datetime import timedelta
from flask import has_request_context, session
from authentication.models import LoginHistory, PasswordResetToken
from core.database import get_session, get_utc_now
from core.exceptions import AuthenticationError, PermissionDeniedError
from core.security import generate_secure_token, verify_password
from users.models import User


class AuthenticationService:
    """Service handling multi-role login, authentication audit, and session control."""

    @staticmethod
    def authenticate_user(
        identifier: str,
        password: str,
        expected_role: str,
        ip_address: str = "127.0.0.1",
        user_agent: str = "Browser",
    ) -> User:
        """Authenticate user credentials and enforce expected role portal boundary."""
        db = get_session()
        clean_id = identifier.strip()

        # Find user by username or email
        user = (
            db.query(User)
            .filter((User.username == clean_id) | (User.email == clean_id.lower()))
            .first()
        )

        history_record = LoginHistory(
            user_id=user.id if user else None,
            attempted_identifier=clean_id,
            role_attempted=expected_role,
            ip_address=ip_address,
            user_agent=user_agent[:250],
            is_successful=False,
        )

        if not user:
            history_record.failure_reason = "User not found"
            db.add(history_record)
            db.commit()
            raise AuthenticationError("Invalid username/email or password.")

        # Check account status & lockouts
        if not user.is_active or user.status == "suspended":
            history_record.failure_reason = "Account suspended/inactive"
            db.add(history_record)
            db.commit()
            raise AuthenticationError("Account is inactive or suspended. Contact administrator.")

        if user.is_locked():
            history_record.failure_reason = "Account locked out"
            db.add(history_record)
            db.commit()
            raise AuthenticationError("Account is temporarily locked due to multiple failed attempts. Please try again later.")

        # Verify password
        if not verify_password(password, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = get_utc_now() + timedelta(minutes=15)
                history_record.failure_reason = "Password incorrect - Account Locked"
            else:
                history_record.failure_reason = "Password incorrect"

            db.add(history_record)
            db.commit()
            raise AuthenticationError("Invalid username/email or password.")

        # Role Boundary Enforcement
        user_role = user.role_name.lower()
        normalized_expected = expected_role.lower()

        if user_role != normalized_expected:
            history_record.failure_reason = f"Role mismatch: actual '{user_role}', tried portal '{normalized_expected}'"
            db.add(history_record)
            db.commit()
            raise PermissionDeniedError(
                f"Access denied: You cannot log into the {expected_role.title()} portal with a {user_role.title()} account. Please use the {user_role.title()} login portal."
            )

        # Successful Login
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login_at = get_utc_now()
        user.login_count += 1

        history_record.is_successful = True
        history_record.failure_reason = None
        db.add(history_record)
        db.commit()

        # Populate Flask Session if running inside request context
        if has_request_context():
            session.clear()
            session["user_id"] = user.id
            session["user_uuid"] = user.uuid
            session["username"] = user.username
            session["user_email"] = user.email
            session["user_name"] = user.full_name
            session["user_role"] = user_role
            session["user_permissions"] = [p.code for p in user.role.permissions] if user.role else []
            session.permanent = True

        return user

    @staticmethod
    def logout():
        """Terminate active session."""
        session.clear()

    @staticmethod
    def create_password_reset_token(email: str) -> str | None:
        """Create a secure password reset token."""
        db = get_session()
        user = db.query(User).filter_by(email=email.strip().lower()).first()
        if not user:
            return None

        token_str = generate_secure_token(32)
        token_record = PasswordResetToken(
            user_id=user.id,
            token=token_str,
            expires_at=get_utc_now() + timedelta(hours=2),
            is_used=False,
        )
        db.add(token_record)
        db.commit()
        return token_str
