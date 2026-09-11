"""Course lifecycle, curriculum hierarchy, and approval workflow tests."""

import pytest
from courses.services import CourseService
from lessons.services import LessonService
from modules.services import ModuleService


def test_course_creation_and_workflow(db_session, sample_instructor):
    """Test course draft creation, submission, approval, and publishing."""
    _, instructor_profile = sample_instructor

    course = CourseService.create_course(
        code="CS-500",
        title="Distributed Systems Engineering",
        short_description="Build fault-tolerant systems.",
        full_description="Deep dive into consensus, replication, and distributed storage.",
        instructor_id=instructor_profile.id,
        status="draft",
    )
    assert course.id is not None
    assert course.status == "draft"

    # Add module & lesson
    module = ModuleService.create_module(course_id=course.id, title="Module 1: Consensus")
    lesson = LessonService.create_lesson(module_id=module.id, title="Raft Consensus Algorithm", content="Raft consensus notes.")
    assert lesson.id is not None
    assert len(course.modules) == 1
    assert len(course.modules[0].lessons) == 1

    # Submit for approval
    CourseService.submit_for_approval(course.id)
    assert course.status == "pending_approval"

    # Admin approves
    CourseService.approve_course(course.id)
    assert course.status == "approved"

    # Publish
    CourseService.publish_course(course.id)
    assert course.status == "published"
    assert course.is_published is True
