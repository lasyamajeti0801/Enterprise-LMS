"""Lesson completion and student progress tracking models."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class LessonProgress(Base, ModelMixin):
    """Tracks individual student progress and completion per lesson."""

    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("enrollment_id", "lesson_id", name="uq_enrollment_lesson_progress"),)

    enrollment_id = Column(Integer, ForeignKey("course_enrollments.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)

    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    enrollment = relationship("CourseEnrollment", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress_records")

    def __repr__(self):
        status = "COMPLETED" if self.is_completed else "IN_PROGRESS"
        return f"<LessonProgress Lesson:{self.lesson_id} Student:{self.student_id} [{status}]>"
