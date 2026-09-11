"""Grading scheme calculations, GPA scale, and letter grade tests."""

import pytest
from courses.services import CourseService
from grading.services import GradingService, percentage_to_letter_and_gpa


def test_letter_grade_and_gpa_conversions():
    """Verify standard 4.0 academic scale conversion."""
    letter, gpa = percentage_to_letter_and_gpa(95.0)
    assert letter == "A"
    assert gpa == 4.0

    letter, gpa = percentage_to_letter_and_gpa(88.0)
    assert letter == "B+"
    assert gpa == 3.3

    letter, gpa = percentage_to_letter_and_gpa(55.0)
    assert letter == "F"
    assert gpa == 0.0


def test_weighted_grade_calculation(db_session, sample_instructor, sample_student):
    """Test weighted score accumulation across course assessments."""
    from assignments.services import AssignmentService
    _, inst = sample_instructor
    _, std = sample_student

    course = CourseService.create_course(
        code="GRD-101",
        title="Grading Test",
        short_description="Test",
        full_description="Test",
        instructor_id=inst.id,
        status="published",
    )

    # Create assignment
    assign = AssignmentService.create_assignment(course.id, "Homework 1", "Instructions", max_marks=100.0)

    scheme = GradingService.update_scheme(
        course_id=course.id,
        assignment_weight=50.0,
        quiz_weight=50.0,
        exam_weight=0.0,
        attendance_weight=0.0,
    )
    assert scheme.assignment_weight == 50.0

    # Unsubmitted assignment -> score 0% -> not passed
    grade_rec = GradingService.calculate_student_grade(course.id, std.id)
    assert grade_rec.id is not None
    assert grade_rec.is_passed is False

    # Student submits and gets graded 90%
    sub = AssignmentService.submit_work(assign.id, std.id, "My code submission")
    AssignmentService.grade_submission(sub.id, score=90.0, graded_by=inst.user_id)

    updated_grade = GradingService.calculate_student_grade(course.id, std.id)
    assert updated_grade.total_weighted_score >= 60.0
    assert updated_grade.is_passed is True
