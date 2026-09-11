"""Authentication history and password reset token models."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class LoginHistory(Base, ModelMixin):
    """Audit log of all user authentication attempts."""

    __tablename__ = "login_history"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    attempted_identifier = Column(String(120), nullable=False)
    role_attempted = Column(String(32), nullable=False)
    ip_address = Column(String(45), default="127.0.0.1", nullable=False)
    user_agent = Column(String(255), nullable=True)
    is_successful = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(128), nullable=True)

    user = relationship("User", back_populates="login_history")

    def __repr__(self):
        status = "SUCCESS" if self.is_successful else "FAILED"
        return f"<LoginHistory {self.attempted_identifier} [{status}]>"


class PasswordResetToken(Base, ModelMixin):
    """Cryptographic token for secure local password resets."""

    __tablename__ = "password_reset_tokens"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(128), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

    def is_valid(self) -> bool:
        """Check if reset token is unexpired and unused."""
        return not self.is_used and self.expires_at > get_utc_now()
