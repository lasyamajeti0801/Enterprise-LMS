"""Immutable audit logging models capturing security actions and entity state changes."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class AuditLog(Base, ModelMixin):
    """System-wide audit trail record."""

    __tablename__ = "audit_logs"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(64), index=True, nullable=False)  # e.g., USER_LOGIN, COURSE_APPROVED, GRADE_UPDATED
    entity_type = Column(String(64), index=True, nullable=False)  # User, Course, Grade, Certificate
    entity_id = Column(String(64), nullable=True)

    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), default="127.0.0.1", nullable=False)
    timestamp = Column(DateTime, default=get_utc_now, index=True, nullable=False)
    status = Column(String(32), default="SUCCESS", nullable=False)

    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}:{self.entity_id} [{self.status}]>"
