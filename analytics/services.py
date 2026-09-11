"""Analytics engine calculating platform KPIs, instructor performance metrics, and student progress."""

from sqlalchemy import func
from core.database import get_session
from certificates.models import Certificate
from courses.models import Course
from enrollment.models import CourseEnrollment
from gamification.models import UserPoints
from grading.models import FinalGradeRecord
from instructors.models import InstructorProfile
from students.models import StudentProfile
from submissions.models import AssignmentSubmission
from users.models import User


class AnalyticsService:
    """Operations aggregating real-time analytics for Admin, Instructor, and Student portals."""

    @staticmethod
    def get_admin_analytics() -> dict:
        """Aggregate platform-wide key performance indicators."""
        session = get_session()

        total_students = session.query(StudentProfile).count()
        total_instructors = session.query(InstructorProfile).count()
        total_users = session.query(User).count()
        total_courses = session.query(Course).count()
        published_courses = session.query(Course).filter_by(status="published").count()
        active_enrollments = session.query(CourseEnrollment).filter_by(status="active").count()
        completed_enrollments = session.query(CourseEnrollment).filter_by(status="completed").count()
        certificates_issued = session.query(Certificate).filter_by(is_revoked=False).count()

        # Category distribution
        category_counts = (
            session.query(Course.category, func.count(Course.id))
            .group_by(Course.category)
            .all()
        )
        category_data = [{"category": cat or "General", "count": count} for cat, count in category_counts]

        # Average GPA
        avg_gpa = session.query(func.avg(StudentProfile.gpa)).scalar() or 3.8

        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_instructors": total_instructors,
            "total_courses": total_courses,
            "published_courses": published_courses,
            "active_enrollments": active_enrollments,
            "completed_enrollments": completed_enrollments,
            "certificates_issued": certificates_issued,
            "category_data": category_data,
            "average_gpa": round(float(avg_gpa), 2),
        }

    @staticmethod
    def get_instructor_analytics(instructor_id: int) -> dict:
        """Aggregate performance metrics for an instructor's courses."""
        session = get_session()

        courses = session.query(Course).filter_by(instructor_id=instructor_id).all()
        course_ids = [c.id for c in courses]

        total_courses = len(courses)
        if not course_ids:
            return {
                "total_courses": 0,
                "total_students": 0,
                "pending_assignments": 0,
                "completion_rate": 0.0,
                "average_score": 0.0,
                "course_stats": [],
            }

        total_enrollments = (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id.in_(course_ids))
            .count()
        )
        completed_count = (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id.in_(course_ids), CourseEnrollment.status == "completed")
            .count()
        )
        completion_rate = round((completed_count / total_enrollments * 100.0) if total_enrollments > 0 else 0.0, 1)

        from assignments.models import Assignment
        pending_assignments = (
            session.query(AssignmentSubmission)
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .filter(
                Assignment.course_id.in_(course_ids),
                AssignmentSubmission.status == "submitted",
            )
            .count()
        )

        avg_score = (
            session.query(func.avg(FinalGradeRecord.total_weighted_score))
            .filter(FinalGradeRecord.course_id.in_(course_ids))
            .scalar()
            or 85.0
        )

        course_stats = []
        for c in courses:
            c_enrollments = len(c.enrollments)
            c_completed = sum(1 for e in c.enrollments if e.status == "completed")
            course_stats.append({
                "id": c.id,
                "code": c.code,
                "title": c.title,
                "status": c.status,
                "enrollments": c_enrollments,
                "completed": c_completed,
            })

        return {
            "total_courses": total_courses,
            "total_students": total_enrollments,
            "pending_assignments": pending_assignments,
            "completion_rate": completion_rate,
            "average_score": round(float(avg_score), 1),
            "course_stats": course_stats,
        }

    @staticmethod
    def get_student_analytics(student_id: int) -> dict:
        """Aggregate personal academic progress metrics for a student."""
        session = get_session()
        student = session.query(StudentProfile).filter_by(id=student_id).first()
        if not student:
            return {}

        enrollments = session.query(CourseEnrollment).filter_by(student_id=student_id).all()
        total_courses = len(enrollments)
        active_courses = sum(1 for e in enrollments if e.status == "active")
        completed_courses = sum(1 for e in enrollments if e.status == "completed")
        certificates_count = session.query(Certificate).filter_by(student_id=student_id, is_revoked=False).count()

        avg_progress = (
            sum(e.progress_percentage for e in enrollments) / total_courses if total_courses > 0 else 0.0
        )

        user_points = session.query(UserPoints).filter_by(user_id=student.user_id).first()
        xp = user_points.total_xp if user_points else 0
        level = user_points.current_level if user_points else 1
        streak = user_points.current_streak_days if user_points else 1

        return {
            "student_number": student.student_id_number,
            "total_courses": total_courses,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "certificates_count": certificates_count,
            "average_progress": round(avg_progress, 1),
            "gpa": student.gpa,
            "total_credits": student.total_credits,
            "xp": xp,
            "level": level,
            "streak": streak,
        }
