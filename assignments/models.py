"""Assignment domain models for course projects, homework, and lab exercises."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class Assignment(Base, ModelMixin):
    """Course assignment entity."""

    __tablename__ = "assignments"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    module_id = Column(Integer, ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)

    max_marks = Column(Float, default=100.0, nullable=False)
    due_date = Column(DateTime, nullable=False)
    allow_late = Column(Boolean, default=True, nullable=False)
    late_penalty_percentage = Column(Float, default=10.0, nullable=False)
    max_attempts = Column(Integer, default=2, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="assignments")
    module = relationship("CourseModule", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assignment {self.id}: {self.title} Due:{self.due_date}>"
