"""Internal in-app notification models."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class Notification(Base, ModelMixin):
    """In-app alert notification delivered to a user."""

    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(32), default="System", nullable=False)  # Course, Assessment, Grade, System, Enrollment
    action_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False, index=True, nullable=False)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        status = "READ" if self.is_read else "UNREAD"
        return f"<Notification User:{self.user_id} [{status}] {self.title}>"
