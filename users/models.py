"""Enterprise User domain model with status, lockouts, and role associations."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class User(Base, ModelMixin):
    """Core user account representing Administrators, Instructors, and Students."""

    __tablename__ = "users"

    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    phone_number = Column(String(32), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # Status: 'active', 'inactive', 'suspended', 'pending_approval'
    status = Column(String(32), default="active", index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Role Association
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    role = relationship("Role", back_populates="users", lazy="joined")

    # Security & Tracking
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    instructor_profile = relationship("InstructorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan", order_by="desc(LoginHistory.created_at)")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        """Return formatted full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def role_name(self) -> str:
        """Return role name."""
        return self.role.name if self.role else "student"

    def has_role(self, role_name: str) -> bool:
        """Check if user belongs to given role."""
        return self.role_name.lower() == role_name.lower()

    def has_permission(self, permission_code: str) -> bool:
        """Check if user's role has the requested permission."""
        if not self.role:
            return False
        return self.role.has_permission(permission_code)

    def is_locked(self) -> bool:
        """Determine if user account is currently locked due to failed login attempts."""
        if self.locked_until and self.locked_until > get_utc_now():
            return True
        return False

    def __repr__(self):
        return f"<User {self.username} [{self.role_name}]>"
