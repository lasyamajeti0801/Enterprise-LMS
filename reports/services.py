"""Reusable reporting engine exporting datasets to CSV, JSON, and formatted tables."""

import csv
import io
import json
from core.database import get_session
from audit.models import AuditLog
from courses.models import Course
from enrollment.models import CourseEnrollment
from grading.models import FinalGradeRecord
from students.models import StudentProfile


class ReportService:
    """Operations generating and exporting institutional reports."""

    @staticmethod
    def export_students_csv() -> str:
        """Export all registered students to CSV formatted string."""
        session = get_session()
        students = session.query(StudentProfile).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student ID", "Full Name", "Email", "Major", "Enrollment Year", "GPA", "Academic Standing"])

        for s in students:
            writer.writerow([
                s.student_id_number,
                s.user.full_name if s.user else "N/A",
                s.user.email if s.user else "N/A",
                s.major,
                s.enrollment_year,
                s.gpa,
                s.academic_standing,
            ])
        return output.getvalue()

    @staticmethod
    def export_courses_csv() -> str:
        """Export all courses to CSV formatted string."""
        session = get_session()
        courses = session.query(Course).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Course Code", "Title", "Category", "Difficulty", "Instructor", "Status", "Enrollments", "Passing Grade"])

        for c in courses:
            instructor_name = c.instructor.user.full_name if c.instructor and c.instructor.user else "Unassigned"
            writer.writerow([
                c.code,
                c.title,
                c.category,
                c.difficulty,
                instructor_name,
                c.status,
                c.active_enrollment_count,
                f"{c.passing_grade}%",
            ])
        return output.getvalue()

    @staticmethod
    def export_grades_csv(course_id: int = None) -> str:
        """Export final grades to CSV."""
        session = get_session()
        query = session.query(FinalGradeRecord)
        if course_id:
            query = query.filter_by(course_id=course_id)
        records = query.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Course Code", "Student ID", "Student Name", "Assignment Score", "Quiz Score", "Exam Score", "Attendance Score", "Final Score", "Grade", "GPA", "Status"])

        for r in records:
            writer.writerow([
                r.course.code if r.course else "N/A",
                r.student.student_id_number if r.student else "N/A",
                r.student.user.full_name if r.student and r.student.user else "N/A",
                r.assignment_score,
                r.quiz_score,
                r.exam_score,
                r.attendance_score,
                f"{r.total_weighted_score}%",
                r.letter_grade,
                r.gpa_value,
                "Passed" if r.is_passed else "Failed",
            ])
        return output.getvalue()

    @staticmethod
    def export_audit_logs_json() -> str:
        """Export audit logs as formatted JSON string."""
        session = get_session()
        logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
        data = [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "user": log.user.username if log.user else "System",
                "timestamp": log.timestamp.isoformat(),
                "status": log.status,
                "ip_address": log.ip_address,
            }
            for log in logs
        ]
        return json.dumps(data, indent=2)
