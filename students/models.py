"""Student domain model and profile."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class StudentProfile(Base, ModelMixin):
    """Extended profile information for enrolled students."""

    __tablename__ = "student_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id_number = Column(String(32), unique=True, index=True, nullable=False)
    major = Column(String(128), default="General Studies", nullable=False)
    enrollment_year = Column(Integer, default=2026, nullable=False)
    academic_standing = Column(String(32), default="Good Standing", nullable=False)  # Good Standing, Honor Roll, Probation

    gpa = Column(Float, default=4.0, nullable=False)
    total_credits = Column(Integer, default=0, nullable=False)

    learning_goals = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    enrollments = relationship("CourseEnrollment", back_populates="student", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    exam_attempts = relationship("ExamAttempt", back_populates="student", cascade="all, delete-orphan")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudentProfile {self.student_id_number}>"
