"""Certificate generation, eligibility checks, and verification tests."""

import os
import pytest
from certificates.services import CertificateService
from core.exceptions import CertificateIneligibleError
from courses.services import CourseService
from enrollment.services import EnrollmentService
from lessons.services import LessonService
from modules.services import ModuleService
from progress.services import ProgressService


def test_certificate_eligibility_and_generation(db_session, sample_instructor, sample_student):
    """Verify that student receives PDF certificate only after satisfying 100% completion & pass grade."""
    _, inst = sample_instructor
    _, std = sample_student

    course = CourseService.create_course(
        code="CERT-101",
        title="Accredited Certification Course",
        short_description="Test",
        full_description="Test",
        instructor_id=inst.id,
        status="published",
    )
    module = ModuleService.create_module(course_id=course.id, title="Module 1")
    lesson = LessonService.create_lesson(module_id=module.id, title="Lesson 1", content="Content")

    enrollment = EnrollmentService.enroll_student(course.id, std.id)

    # Ineligible initially (progress 0%)
    is_eligible, _ = CertificateService.check_eligibility(course.id, std.id)
    assert is_eligible is False

    with pytest.raises(CertificateIneligibleError):
        CertificateService.generate_certificate(course.id, std.id)

    # Complete lesson -> 100%
    ProgressService.mark_lesson_completed(enrollment.id, lesson.id)

    # Now eligible -> generate local PDF certificate
    cert = CertificateService.generate_certificate(course.id, std.id)
    assert cert.certificate_number is not None
    assert cert.verification_code is not None
    assert os.path.exists(cert.pdf_file_path)

    # Verify certificate via public verification service
    verification = CertificateService.verify_certificate(cert.verification_code)
    assert verification is not None
    assert verification["is_valid"] is True
    assert verification["course_code"] == "CERT-101"
