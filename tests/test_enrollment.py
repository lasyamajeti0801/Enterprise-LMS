"""Enrollment constraints, capacity checks, and progress calculation tests."""

import pytest
from core.exceptions import EnrollmentError
from courses.services import CourseService
from enrollment.services import EnrollmentService
from lessons.services import LessonService
from modules.services import ModuleService
from progress.services import ProgressService


def test_enrollment_and_capacity_limits(db_session, sample_instructor, sample_student):
    """Verify student enrollment and capacity constraints."""
    _, inst = sample_instructor
    _, std = sample_student

    # Create published course with capacity of 1
    course = CourseService.create_course(
        code="CAP-101",
        title="Exclusive Seminar",
        short_description="Limited seats",
        full_description="One seat only",
        instructor_id=inst.id,
        capacity=1,
        status="published",
    )

    # First student enrolls
    e1 = EnrollmentService.enroll_student(course.id, std.id)
    assert e1.status == "active"
    assert course.is_full is True

    # Duplicate enrollment check
    with pytest.raises(EnrollmentError):
        EnrollmentService.enroll_student(course.id, std.id)


def test_progress_calculation(db_session, sample_instructor, sample_student):
    """Verify hierarchical progress percentage calculation."""
    _, inst = sample_instructor
    _, std = sample_student

    course = CourseService.create_course(
        code="PRG-101",
        title="Progress Test Course",
        short_description="Test",
        full_description="Test",
        instructor_id=inst.id,
        status="published",
    )
    module = ModuleService.create_module(course_id=course.id, title="Module 1")
    l1 = LessonService.create_lesson(module_id=module.id, title="Lesson 1", content="Content 1")
    l2 = LessonService.create_lesson(module_id=module.id, title="Lesson 2", content="Content 2")

    enrollment = EnrollmentService.enroll_student(course.id, std.id)
    assert enrollment.progress_percentage == 0.0

    # Complete 1 out of 2 lessons -> 50%
    res1 = ProgressService.mark_lesson_completed(enrollment.id, l1.id)
    assert res1["course_progress"] == 50.0

    # Complete 2nd lesson -> 100% and marked completed
    res2 = ProgressService.mark_lesson_completed(enrollment.id, l2.id)
    assert res2["course_progress"] == 100.0
    assert res2["status"] == "completed"
