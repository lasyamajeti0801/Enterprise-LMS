"""Question bank and automated quiz evaluation tests."""

import pytest
from courses.services import CourseService
from question_bank.services import QuestionBankService
from quizzes.services import QuizService


def test_question_evaluation_and_quiz_grading(db_session, sample_instructor, sample_student):
    """Test question bank items and automated quiz attempt scoring."""
    _, inst = sample_instructor
    _, std = sample_student

    course = CourseService.create_course(
        code="QZ-101",
        title="Quiz Course",
        short_description="Test",
        full_description="Test",
        instructor_id=inst.id,
        status="published",
    )

    q1 = QuestionBankService.create_question(
        prompt="What is 2 + 2?",
        question_type="mcq_single",
        options=["3", "4", "5"],
        correct_answers=["4"],
        marks=10.0,
    )

    quiz = QuizService.create_quiz(
        course_id=course.id,
        title="Math Basics Quiz",
        passing_percentage=60.0,
    )
    QuizService.add_question_to_quiz(quiz.id, q1.id)

    # Start attempt
    attempt = QuizService.start_quiz_attempt(quiz.id, std.id)
    assert attempt.status == "in_progress"

    # Submit correct answer
    evaluated_attempt = QuizService.submit_quiz_attempt(attempt.id, {q1.id: "4"})
    assert evaluated_attempt.score == 10.0
    assert evaluated_attempt.percentage == 100.0
    assert evaluated_attempt.is_passed is True
    assert evaluated_attempt.status == "evaluated"
