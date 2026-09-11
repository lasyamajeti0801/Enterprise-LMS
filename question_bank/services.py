"""Question bank services for managing reusable questions."""

from core.database import get_session
from core.exceptions import ResourceNotFoundError
from core.pagination import paginate_query
from question_bank.models import QuestionBankItem, QuestionCategory


class QuestionBankService:
    """Operations managing categorized question banks and items."""

    @staticmethod
    def create_category(name: str, description: str = "") -> QuestionCategory:
        """Create or get a question category."""
        session = get_session()
        cat = session.query(QuestionCategory).filter_by(name=name.strip()).first()
        if not cat:
            cat = QuestionCategory(name=name.strip(), description=description.strip())
            session.add(cat)
            session.commit()
        return cat

    @staticmethod
    def create_question(
        prompt: str,
        question_type: str = "mcq_single",
        options: list = None,
        correct_answers: list = None,
        category_name: str = "General",
        explanation: str = "",
        marks: float = 1.0,
        negative_marks: float = 0.0,
        difficulty: str = "Medium",
        tags: str = "",
    ) -> QuestionBankItem:
        """Create and store a reusable question item."""
        session = get_session()
        category = QuestionBankService.create_category(category_name)

        q = QuestionBankItem(
            category_id=category.id,
            question_type=question_type,
            prompt=prompt.strip(),
            explanation=explanation.strip() if explanation else None,
            marks=float(marks),
            negative_marks=float(negative_marks),
            difficulty=difficulty,
            tags=tags.strip(),
        )
        q.options = options or []
        q.correct_answers = correct_answers or []
        session.add(q)
        session.commit()
        return q

    @staticmethod
    def get_by_id(question_id: int) -> QuestionBankItem:
        """Get question by ID."""
        q = get_session().query(QuestionBankItem).filter_by(id=question_id).first()
        if not q:
            raise ResourceNotFoundError(f"Question {question_id} not found.")
        return q

    @staticmethod
    def list_questions(category_id: int = None, difficulty: str = "", q_type: str = "", page: int = 1, per_page: int = 20):
        """List filtered questions."""
        query = get_session().query(QuestionBankItem)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if q_type:
            query = query.filter_by(question_type=q_type)
        query = query.order_by(QuestionBankItem.id.desc())
        return paginate_query(query, page=page, per_page=per_page)
