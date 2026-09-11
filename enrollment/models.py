"""Course Enrollment domain model representing student registrations and status transitions."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class CourseEnrollment(Base, ModelMixin):
    """Enrollment of a student in a course with completion and grading records."""

    __tablename__ = "course_enrollments"
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="uq_course_student_enrollment"),)

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    # Status: 'active', 'completed', 'dropped', 'suspended', 'pending_approval'
    status = Column(String(32), default="active", index=True, nullable=False)
    enrollment_date = Column(DateTime, default=get_utc_now, nullable=False)
    completion_date = Column(DateTime, nullable=True)

    progress_percentage = Column(Float, default=0.0, nullable=False)
    final_grade = Column(Float, nullable=True)
    letter_grade = Column(String(8), nullable=True)
    is_certified = Column(Boolean, default=False, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="enrollments")
    student = relationship("StudentProfile", back_populates="enrollments")
    lesson_progress = relationship("LessonProgress", back_populates="enrollment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CourseEnrollment Course:{self.course_id} Student:{self.student_id} [{self.status}]>"
