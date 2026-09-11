"""Question Bank domain models supporting diverse question types, scoring, and taxonomies."""

import json
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class QuestionCategory(Base, ModelMixin):
    """Categorization for question bank items (e.g., Algorithms, Data Structures, Security)."""

    __tablename__ = "question_categories"

    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    questions = relationship("QuestionBankItem", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuestionCategory {self.name}>"


class QuestionBankItem(Base, ModelMixin):
    """Reusable assessment question entity."""

    __tablename__ = "question_bank_items"

    category_id = Column(Integer, ForeignKey("question_categories.id", ondelete="SET NULL"), nullable=True)
    
    # Types: 'mcq_single', 'mcq_multi', 'true_false', 'short_answer', 'fill_blank'
    question_type = Column(String(32), default="mcq_single", nullable=False)
    prompt = Column(Text, nullable=False)
    
    # JSON strings for options and answers
    _options_json = Column("options_json", Text, default="[]", nullable=False)
    _correct_answers_json = Column("correct_answers_json", Text, default="[]", nullable=False)
    
    explanation = Column(Text, nullable=True)
    marks = Column(Float, default=1.0, nullable=False)
    negative_marks = Column(Float, default=0.0, nullable=False)
    difficulty = Column(String(32), default="Medium", nullable=False)  # Easy, Medium, Hard
    tags = Column(String(255), nullable=True)

    # Relationships
    category = relationship("QuestionCategory", back_populates="questions")
    quiz_associations = relationship("QuizQuestion", back_populates="question", cascade="all, delete-orphan")

    @property
    def options(self) -> list:
        """Parse options from JSON."""
        try:
            return json.loads(self._options_json) if self._options_json else []
        except Exception:
            return []

    @options.setter
    def options(self, val: list):
        self._options_json = json.dumps(val)

    @property
    def correct_answers(self) -> list:
        """Parse correct answers from JSON."""
        try:
            return json.loads(self._correct_answers_json) if self._correct_answers_json else []
        except Exception:
            return []

    @correct_answers.setter
    def correct_answers(self, val: list):
        self._correct_answers_json = json.dumps(val)

    def evaluate_answer(self, student_answer) -> tuple[bool, float]:
        """Evaluate student answer against correct answers and calculate awarded marks."""
        if not student_answer:
            return False, -self.negative_marks if self.negative_marks else 0.0

        q_type = self.question_type.lower()

        if q_type in ("mcq_single", "true_false", "short_answer", "fill_blank"):
            student_clean = str(student_answer).strip().lower()
            correct_clean = [str(a).strip().lower() for a in self.correct_answers]
            if student_clean in correct_clean:
                return True, self.marks
            return False, -self.negative_marks

        elif q_type == "mcq_multi":
            if not isinstance(student_answer, list):
                student_answer = [student_answer]
            student_set = {str(a).strip().lower() for a in student_answer}
            correct_set = {str(a).strip().lower() for a in self.correct_answers}
            if student_set == correct_set:
                return True, self.marks
            return False, -self.negative_marks

        return False, 0.0

    def __repr__(self):
        return f"<QuestionBankItem {self.id} [{self.question_type} - {self.difficulty}]>"
