"""Examination authoring, scheduling, and evaluation services."""

from core.database import get_session, get_utc_now
from core.exceptions import AssessmentError, ResourceNotFoundError
from core.pagination import paginate_query
from examinations.models import Exam, ExamAnswer, ExamAttempt


class ExaminationService:
    """Operations managing formal midterm, final, and certification exams."""

    @staticmethod
    def create_exam(
        course_id: int,
        title: str,
        exam_type: str = "Final",
        duration_minutes: int = 60,
        total_marks: float = 100.0,
        passing_marks: float = 60.0,
        instructions: str = "",
        start_window=None,
        end_window=None,
    ) -> Exam:
        """Create a scheduled formal examination."""
        session = get_session()
        exam = Exam(
            course_id=course_id,
            title=title.strip(),
            exam_type=exam_type,
            duration_minutes=duration_minutes,
            total_marks=total_marks,
            passing_marks=passing_marks,
            instructions=instructions.strip() if instructions else None,
            start_window=start_window,
            end_window=end_window,
            is_published=True,
        )
        session.add(exam)
        session.commit()
        return exam

    @staticmethod
    def get_by_id(exam_id: int) -> Exam:
        """Fetch exam by ID."""
        exam = get_session().query(Exam).filter_by(id=exam_id).first()
        if not exam:
            raise ResourceNotFoundError(f"Exam {exam_id} not found.")
        return exam

    @staticmethod
    def start_exam_attempt(exam_id: int, student_id: int) -> ExamAttempt:
        """Start an exam session for a student."""
        session = get_session()
        exam = ExaminationService.get_by_id(exam_id)

        prior_attempts = (
            session.query(ExamAttempt)
            .filter_by(exam_id=exam_id, student_id=student_id)
            .count()
        )

        if prior_attempts >= 1:
            raise AssessmentError("Only 1 attempt is permitted for formal examinations.")

        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=student_id,
            attempt_number=prior_attempts + 1,
            start_time=get_utc_now(),
            status="in_progress",
        )
        session.add(attempt)
        session.commit()
        return attempt

    @staticmethod
    def grade_exam_attempt(attempt_id: int, total_score: float, evaluator_id: int) -> ExamAttempt:
        """Instructor submits official grade for an exam attempt."""
        session = get_session()
        attempt = session.query(ExamAttempt).filter_by(id=attempt_id).first()
        if not attempt:
            raise ResourceNotFoundError(f"Exam attempt {attempt_id} not found.")

        attempt.score = round(float(total_score), 2)
        attempt.is_evaluated = True
        attempt.status = "graded"
        attempt.evaluator_id = evaluator_id
        session.commit()
        return attempt
