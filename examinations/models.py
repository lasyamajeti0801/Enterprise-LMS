"""Examination models for scheduled midterm, final, and certification exams."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class Exam(Base, ModelMixin):
    """Formal course examination with scheduled availability and rubric evaluations."""

    __tablename__ = "examinations"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    exam_type = Column(String(32), default="Final", nullable=False)  # Midterm, Final, Comprehensive, Certification

    start_window = Column(DateTime, nullable=True)
    end_window = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=60, nullable=False)

    total_marks = Column(Float, default=100.0, nullable=False)
    passing_marks = Column(Float, default=60.0, nullable=False)
    instructions = Column(Text, nullable=True)
    is_published = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="exams")
    attempts = relationship("ExamAttempt", back_populates="exam", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exam {self.id}: {self.title} ({self.exam_type})>"


class ExamAttempt(Base, ModelMixin):
    """Student examination session."""

    __tablename__ = "exam_attempts"

    exam_id = Column(Integer, ForeignKey("examinations.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)

    start_time = Column(DateTime, default=get_utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)

    score = Column(Float, default=0.0, nullable=False)
    is_evaluated = Column(Boolean, default=False, nullable=False)
    status = Column(String(32), default="in_progress", nullable=False)  # 'in_progress', 'submitted', 'evaluated'
    evaluator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    exam = relationship("Exam", back_populates="attempts")
    student = relationship("StudentProfile", back_populates="exam_attempts")
    answers = relationship("ExamAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExamAttempt {self.id} Student:{self.student_id} Score:{self.score}/{self.exam.total_marks if self.exam else 100}>"


class ExamAnswer(Base, ModelMixin):
    """Student answer response to an examination section or question."""

    __tablename__ = "exam_answers"

    attempt_id = Column(Integer, ForeignKey("exam_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank_items.id", ondelete="CASCADE"), index=True, nullable=False)

    answer_text = Column(Text, nullable=True)
    score_awarded = Column(Float, default=0.0, nullable=False)
    is_evaluated = Column(Boolean, default=False, nullable=False)
    evaluator_remarks = Column(Text, nullable=True)

    attempt = relationship("ExamAttempt", back_populates="answers")
    question = relationship("QuestionBankItem")
