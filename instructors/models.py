"""Instructor domain model and profile."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class InstructorProfile(Base, ModelMixin):
    """Extended profile information for course instructors."""

    __tablename__ = "instructor_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(32), unique=True, index=True, nullable=False)
    title = Column(String(64), default="Instructor", nullable=False)  # Professor, Lecturer, Lead Instructor
    department = Column(String(128), default="Computer Science & Engineering", nullable=False)
    office_location = Column(String(128), nullable=True)
    qualifications = Column(Text, nullable=True)
    expertise_areas = Column(String(255), nullable=True)

    # Status: 'pending_approval', 'approved', 'rejected', 'active'
    approval_status = Column(String(32), default="approved", index=True, nullable=False)
    rating = Column(Float, default=5.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="instructor_profile")
    courses = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InstructorProfile {self.employee_id} ({self.title})>"
