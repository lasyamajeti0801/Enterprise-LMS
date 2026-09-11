"""Certificate domain model for verified credentials and local PDF generation."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class Certificate(Base, ModelMixin):
    """Accredited certificate issued upon successful course completion."""

    __tablename__ = "certificates"
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="uq_course_student_certificate"),)

    certificate_number = Column(String(64), unique=True, index=True, nullable=False)
    verification_code = Column(String(64), unique=True, index=True, nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)

    issue_date = Column(DateTime, default=get_utc_now, nullable=False)
    final_grade_percentage = Column(Float, default=100.0, nullable=False)
    pdf_file_path = Column(String(255), nullable=True)

    is_revoked = Column(Boolean, default=False, nullable=False)
    revocation_reason = Column(Text, nullable=True)

    course = relationship("Course", back_populates="certificates")
    student = relationship("StudentProfile", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate {self.certificate_number} Student:{self.student_id} Course:{self.course_id}>"
