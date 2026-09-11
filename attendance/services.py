"""Attendance management services and percentage calculations."""

from datetime import date
from core.database import get_session
from core.exceptions import ResourceNotFoundError
from core.pagination import paginate_query
from attendance.models import AttendanceRecord, AttendanceSession
from enrollment.models import CourseEnrollment
from students.models import StudentProfile


class AttendanceService:
    """Operations managing attendance sessions, student attendance logging, and percentage reports."""

    @staticmethod
    def create_session(
        course_id: int,
        title: str,
        session_date: date,
        start_time: str = "09:00",
        end_time: str = "10:30",
        description: str = "",
    ) -> AttendanceSession:
        """Create a new attendance tracking session."""
        session = get_session()
        att_session = AttendanceSession(
            course_id=course_id,
            title=title.strip(),
            session_date=session_date,
            start_time=start_time,
            end_time=end_time,
            description=description.strip(),
        )
        session.add(att_session)
        session.commit()
        return att_session

    @staticmethod
    def record_attendance(
        session_id: int,
        student_id: int,
        status: str = "present",
        remarks: str = "",
        recorded_by: int = None,
    ) -> AttendanceRecord:
        """Record or update attendance for an individual student."""
        session = get_session()
        record = (
            session.query(AttendanceRecord)
            .filter_by(session_id=session_id, student_id=student_id)
            .first()
        )

        if not record:
            record = AttendanceRecord(
                session_id=session_id,
                student_id=student_id,
                status=status.lower(),
                remarks=remarks.strip() if remarks else None,
                recorded_by=recorded_by,
            )
            session.add(record)
        else:
            record.status = status.lower()
            if remarks:
                record.remarks = remarks.strip()
            if recorded_by:
                record.recorded_by = recorded_by

        session.commit()
        return record

    @staticmethod
    def bulk_record_attendance(session_id: int, attendance_data: dict, recorded_by: int = None):
        """Record attendance for multiple students in batch (student_id -> status)."""
        session = get_session()
        for student_id, status in attendance_data.items():
            AttendanceService.record_attendance(
                session_id=int(student_id),
                student_id=int(student_id),
                status=status,
                recorded_by=recorded_by,
            )
        session.commit()

    @staticmethod
    def get_student_course_attendance(course_id: int, student_id: int) -> dict:
        """Calculate attendance summary and percentage for a student in a course."""
        session = get_session()

        all_sessions = session.query(AttendanceSession).filter_by(course_id=course_id).all()
        total_sessions = len(all_sessions)

        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "present": 0,
                "absent": 0,
                "late": 0,
                "excused": 0,
                "percentage": 100.0,
                "is_eligible": True,
            }

        session_ids = [s.id for s in all_sessions]
        records = (
            session.query(AttendanceRecord)
            .filter(AttendanceRecord.session_id.in_(session_ids), AttendanceRecord.student_id == student_id)
            .all()
        )

        present = sum(1 for r in records if r.status == "present")
        late = sum(1 for r in records if r.status == "late")
        excused = sum(1 for r in records if r.status == "excused")
        recorded_total = len(records)
        absent = (total_sessions - recorded_total) + sum(1 for r in records if r.status == "absent")

        # Weighted calculation: Present=1.0, Late=0.8, Excused=1.0
        effective_attended = present + (late * 0.8) + (excused * 1.0)
        percentage = round((effective_attended / total_sessions) * 100.0, 1)

        return {
            "total_sessions": total_sessions,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "percentage": percentage,
            "is_eligible": percentage >= 75.0,
        }

    @staticmethod
    def get_course_sessions(course_id: int, page: int = 1, per_page: int = 20):
        """Retrieve paginated sessions for a course."""
        query = (
            get_session()
            .query(AttendanceSession)
            .filter_by(course_id=course_id)
            .order_by(AttendanceSession.session_date.desc())
        )
        return paginate_query(query, page=page, per_page=per_page)
