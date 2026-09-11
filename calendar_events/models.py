"""Academic calendar event models for course schedules, deadlines, and live sessions."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class CalendarEvent(Base, ModelMixin):
    """Calendar event entity for course schedules and milestones."""

    __tablename__ = "calendar_events"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(32), default="Class", nullable=False)  # Class, Exam, Assignment, Holiday, Webinar

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location_or_link = Column(String(255), nullable=True)

    course = relationship("Course")
    user = relationship("User")

    def __repr__(self):
        return f"<CalendarEvent {self.title} at {self.start_time}>"
