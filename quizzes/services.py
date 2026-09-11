"""Quiz authoring, evaluation, and attempt management engine."""

import random
from core.database import get_session, get_utc_now
from core.events import events
from core.exceptions import AssessmentError, ResourceNotFoundError
from core.pagination import paginate_query
from question_bank.models import QuestionBankItem
from quizzes.models import Quiz, QuizAnswer, QuizAttempt, QuizQuestion


class QuizService:
    """Operations managing quizzes and automated grading of student attempts."""

    @staticmethod
    def create_quiz(
        course_id: int,
        title: str,
        description: str = "",
        instructions: str = "",
        module_id: int = None,
        time_limit_minutes: int = 20,
        passing_percentage: float = 60.0,
        max_attempts: int = 3,
        shuffle_questions: bool = True,
        show_correct_answers: bool = True,
    ) -> Quiz:
        """Create a new quiz."""
        session = get_session()
        quiz = Quiz(
            course_id=course_id,
            module_id=module_id,
            title=title.strip(),
            description=description.strip() if description else None,
            instructions=instructions.strip() if instructions else None,
            time_limit_minutes=time_limit_minutes,
            passing_percentage=passing_percentage,
            max_attempts=max_attempts,
            shuffle_questions=shuffle_questions,
            show_correct_answers=show_correct_answers,
            is_published=True,
        )
        session.add(quiz)
        session.commit()
        return quiz

    @staticmethod
    def add_question_to_quiz(quiz_id: int, question_id: int, marks_override: float = None) -> QuizQuestion:
        """Link a question bank item to a quiz."""
        session = get_session()
        max_idx = session.query(QuizQuestion).filter_by(quiz_id=quiz_id).count()
        qq = QuizQuestion(
            quiz_id=quiz_id,
            question_id=question_id,
            order_index=max_idx + 1,
            marks_override=marks_override,
        )
        session.add(qq)
        session.commit()
        return qq

    @staticmethod
    def get_by_id(quiz_id: int) -> Quiz:
        """Fetch quiz by ID."""
        quiz = get_session().query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            raise ResourceNotFoundError(f"Quiz {quiz_id} not found.")
        return quiz

    @staticmethod
    def start_quiz_attempt(quiz_id: int, student_id: int) -> QuizAttempt:
        """Initiate a new quiz attempt session for a student."""
        session = get_session()
        quiz = QuizService.get_by_id(quiz_id)

        prior_attempts = (
            session.query(QuizAttempt)
            .filter_by(quiz_id=quiz_id, student_id=student_id)
            .count()
        )

        if prior_attempts >= quiz.max_attempts:
            raise AssessmentError(f"Maximum attempt limit ({quiz.max_attempts}) reached for this quiz.")

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            attempt_number=prior_attempts + 1,
            start_time=get_utc_now(),
            max_score=quiz.total_marks,
            status="in_progress",
        )
        session.add(attempt)
        session.commit()
        return attempt

    @staticmethod
    def submit_quiz_attempt(attempt_id: int, raw_answers: dict) -> QuizAttempt:
        """Grade and finalize a quiz attempt."""
        session = get_session()
        attempt = session.query(QuizAttempt).filter_by(id=attempt_id).first()
        if not attempt:
            raise ResourceNotFoundError(f"Attempt {attempt_id} not found.")

        if attempt.status != "in_progress":
            raise AssessmentError("This attempt has already been submitted and graded.")

        quiz = attempt.quiz
        total_score = 0.0
        max_possible = 0.0

        for qq in quiz.questions:
            q_item = qq.question
            if not q_item:
                continue

            q_weight = qq.marks_override if qq.marks_override is not None else q_item.marks
            max_possible += q_weight

            student_ans = raw_answers.get(str(q_item.id)) or raw_answers.get(q_item.id)
            is_correct, marks_awarded = q_item.evaluate_answer(student_ans)

            # Scale if marks_override was used
            if qq.marks_override is not None and is_correct:
                marks_awarded = qq.marks_override

            total_score += max(0.0, marks_awarded)

            ans_record = QuizAnswer(
                attempt_id=attempt.id,
                question_id=q_item.id,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
            )
            ans_record.student_answer = student_ans
            session.add(ans_record)

        attempt.end_time = get_utc_now()
        attempt.score = round(total_score, 2)
        attempt.max_score = round(max_possible, 2)
        attempt.percentage = round((total_score / max_possible * 100.0) if max_possible > 0 else 0.0, 1)
        attempt.is_passed = attempt.percentage >= quiz.passing_percentage
        attempt.status = "evaluated"

        session.commit()

        # Gamification event if passed
        if attempt.is_passed:
            events.emit(
                "quiz_passed",
                student_id=attempt.student_id,
                quiz_id=attempt.quiz_id,
                percentage=attempt.percentage,
            )

        return attempt

    @staticmethod
    def get_best_attempt(quiz_id: int, student_id: int) -> QuizAttempt | None:
        """Fetch highest scoring attempt for a student."""
        return (
            get_session()
            .query(QuizAttempt)
            .filter_by(quiz_id=quiz_id, student_id=student_id, status="evaluated")
            .order_by(QuizAttempt.score.desc())
            .first()
        )
