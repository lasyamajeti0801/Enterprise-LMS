"""Attendance sessions and student attendance records."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class AttendanceSession(Base, ModelMixin):
    """Lecture or lab session requiring attendance tracking."""

    __tablename__ = "attendance_sessions"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(String(16), default="09:00", nullable=False)
    end_time = Column(String(16), default="10:30", nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    course = relationship("Course", back_populates="attendance_sessions")
    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AttendanceSession {self.title} on {self.session_date}>"


class AttendanceRecord(Base, ModelMixin):
    """Individual student attendance mark for a session."""

    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_session_student_attendance"),)

    session_id = Column(Integer, ForeignKey("attendance_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    # Status: 'present', 'absent', 'late', 'excused'
    status = Column(String(32), default="present", nullable=False)
    remarks = Column(String(255), nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("StudentProfile")

    def __repr__(self):
        return f"<AttendanceRecord Session:{self.session_id} Student:{self.student_id} [{self.status}]>"
