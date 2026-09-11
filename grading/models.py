"""Grading schemes, weighted evaluation models, and final gradebooks."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class GradingScheme(Base, ModelMixin):
    """Configurable weights for course grade components."""

    __tablename__ = "grading_schemes"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), unique=True, nullable=False)

    assignment_weight = Column(Float, default=25.0, nullable=False)  # e.g. 25%
    quiz_weight = Column(Float, default=25.0, nullable=False)        # e.g. 25%
    exam_weight = Column(Float, default=40.0, nullable=False)        # e.g. 40%
    attendance_weight = Column(Float, default=10.0, nullable=False)  # e.g. 10%

    passing_threshold = Column(Float, default=60.0, nullable=False)

    course = relationship("Course", back_populates="grading_scheme")

    def __repr__(self):
        return f"<GradingScheme Course:{self.course_id} A:{self.assignment_weight}% Q:{self.quiz_weight}% E:{self.exam_weight}% Att:{self.attendance_weight}%>"


class FinalGradeRecord(Base, ModelMixin):
    """Calculated and finalized course grade for a student."""

    __tablename__ = "final_grade_records"
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="uq_course_student_grade"),)

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    assignment_score = Column(Float, default=0.0, nullable=False)
    quiz_score = Column(Float, default=0.0, nullable=False)
    exam_score = Column(Float, default=0.0, nullable=False)
    attendance_score = Column(Float, default=0.0, nullable=False)

    total_weighted_score = Column(Float, default=0.0, nullable=False)
    letter_grade = Column(String(8), default="F", nullable=False)
    gpa_value = Column(Float, default=0.0, nullable=False)
    is_passed = Column(Boolean, default=False, nullable=False)
    finalized_at = Column(DateTime, default=get_utc_now, nullable=False)

    course = relationship("Course")
    student = relationship("StudentProfile")

    def __repr__(self):
        return f"<FinalGradeRecord Course:{self.course_id} Student:{self.student_id} Score:{self.total_weighted_score}% ({self.letter_grade})>"
