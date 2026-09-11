"""Enrollment services with capacity checks, status transitions, and history tracking."""

from core.database import get_session, get_utc_now
from core.exceptions import EnrollmentError, ResourceNotFoundError
from core.pagination import paginate_query
from courses.models import Course
from enrollment.models import CourseEnrollment
from students.models import StudentProfile


class EnrollmentService:
    """Operations managing student enrollments in courses."""

    @staticmethod
    def enroll_student(course_id: int, student_id: int) -> CourseEnrollment:
        """Enroll a student in a course with validation."""
        session = get_session()

        course = session.query(Course).filter_by(id=course_id).first()
        if not course:
            raise ResourceNotFoundError(f"Course {course_id} not found.")

        if course.status != "published":
            raise EnrollmentError("Cannot enroll in an unpublished or archived course.")

        if course.is_full:
            raise EnrollmentError(f"Course '{course.title}' has reached its maximum enrollment capacity.")

        # Check existing enrollment
        existing = (
            session.query(CourseEnrollment)
            .filter_by(course_id=course_id, student_id=student_id)
            .first()
        )
        if existing:
            if existing.status == "active":
                raise EnrollmentError("Student is already actively enrolled in this course.")
            elif existing.status in ("dropped", "suspended"):
                existing.status = "active"
                existing.enrollment_date = get_utc_now()
                session.commit()
                return existing

        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student_id,
            status="active",
            enrollment_date=get_utc_now(),
            progress_percentage=0.0,
        )
        session.add(enrollment)
        session.commit()
        return enrollment

    @staticmethod
    def get_enrollment(course_id: int, student_id: int) -> CourseEnrollment | None:
        """Get enrollment record for student and course."""
        return (
            get_session()
            .query(CourseEnrollment)
            .filter_by(course_id=course_id, student_id=student_id)
            .first()
        )

    @staticmethod
    def drop_course(course_id: int, student_id: int) -> CourseEnrollment:
        """Drop enrollment in a course."""
        session = get_session()
        enrollment = EnrollmentService.get_enrollment(course_id, student_id)
        if not enrollment:
            raise ResourceNotFoundError("Enrollment not found.")
        enrollment.status = "dropped"
        session.commit()
        return enrollment

    @staticmethod
    def get_student_enrollments(student_id: int, status: str = "", page: int = 1, per_page: int = 15):
        """List courses a student is enrolled in."""
        query = get_session().query(CourseEnrollment).filter_by(student_id=student_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(CourseEnrollment.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def get_course_enrollments(course_id: int, status: str = "", page: int = 1, per_page: int = 15):
        """List students enrolled in a course."""
        query = get_session().query(CourseEnrollment).filter_by(course_id=course_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(CourseEnrollment.id.desc())
        return paginate_query(query, page=page, per_page=per_page)
