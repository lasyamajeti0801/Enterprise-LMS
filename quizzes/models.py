"""Quiz and Quiz Attempt models for automated student assessments."""

import json
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class Quiz(Base, ModelMixin):
    """Quiz assessment assigned to a course or module."""

    __tablename__ = "quizzes"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    module_id = Column(Integer, ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)

    time_limit_minutes = Column(Integer, default=20, nullable=False)
    passing_percentage = Column(Float, default=60.0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    shuffle_questions = Column(Boolean, default=True, nullable=False)
    show_correct_answers = Column(Boolean, default=True, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="quizzes")
    module = relationship("CourseModule", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order_index")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    @property
    def total_marks(self) -> float:
        """Calculate total marks across all questions in quiz."""
        return sum(qq.question.marks if qq.question else 0.0 for qq in self.questions)

    def __repr__(self):
        return f"<Quiz {self.id}: {self.title}>"


class QuizQuestion(Base, ModelMixin):
    """Association linking QuestionBankItem into a specific Quiz."""

    __tablename__ = "quiz_questions"

    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank_items.id", ondelete="CASCADE"), index=True, nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    marks_override = Column(Float, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
    question = relationship("QuestionBankItem", back_populates="quiz_associations")

    def __repr__(self):
        return f"<QuizQuestion Quiz:{self.quiz_id} Question:{self.question_id}>"


class QuizAttempt(Base, ModelMixin):
    """Student attempt session for a quiz."""

    __tablename__ = "quiz_attempts"

    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)

    start_time = Column(DateTime, default=get_utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)

    score = Column(Float, default=0.0, nullable=False)
    max_score = Column(Float, default=0.0, nullable=False)
    percentage = Column(Float, default=0.0, nullable=False)
    is_passed = Column(Boolean, default=False, nullable=False)
    status = Column(String(32), default="in_progress", nullable=False)  # 'in_progress', 'submitted', 'evaluated'

    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("StudentProfile", back_populates="quiz_attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizAttempt {self.id} Student:{self.student_id} Score:{self.score}/{self.max_score}>"


class QuizAnswer(Base, ModelMixin):
    """Individual question answer submitted during a quiz attempt."""

    __tablename__ = "quiz_answers"

    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank_items.id", ondelete="CASCADE"), index=True, nullable=False)

    _student_answer_json = Column("student_answer_json", Text, nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    marks_awarded = Column(Float, default=0.0, nullable=False)
    feedback = Column(Text, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("QuestionBankItem")

    @property
    def student_answer(self):
        try:
            return json.loads(self._student_answer_json) if self._student_answer_json else None
        except Exception:
            return self._student_answer_json

    @student_answer.setter
    def student_answer(self, val):
        self._student_answer_json = json.dumps(val)
