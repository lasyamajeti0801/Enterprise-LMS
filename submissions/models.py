"""Assignment submission domain models."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class AssignmentSubmission(Base, ModelMixin):
    """Student submission record for an assignment with grading and feedback."""

    __tablename__ = "assignment_submissions"

    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)

    submission_text = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    submitted_at = Column(DateTime, default=get_utc_now, nullable=False)
    is_late = Column(Boolean, default=False, nullable=False)

    score = Column(Float, nullable=True)
    letter_grade = Column(String(8), nullable=True)
    instructor_feedback = Column(Text, nullable=True)
    graded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    # Status: 'submitted', 'graded', 'resubmission_requested'
    status = Column(String(32), default="submitted", index=True, nullable=False)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="assignment_submissions")
    grader = relationship("User")

    def __repr__(self):
        return f"<AssignmentSubmission Assignment:{self.assignment_id} Student:{self.student_id} Score:{self.score}>"
