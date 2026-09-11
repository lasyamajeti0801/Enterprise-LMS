"""Course domain model with categorization, workflow status, and relationship definitions."""

import re
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


def slugify(text: str) -> str:
    """Generate a clean URL slug from text."""
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


class Course(Base, ModelMixin):
    """Core Course entity representing an educational or training curriculum."""

    __tablename__ = "courses"

    code = Column(String(32), unique=True, index=True, nullable=False)  # e.g., CS-101
    title = Column(String(200), index=True, nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    short_description = Column(String(500), nullable=False)
    full_description = Column(Text, nullable=False)
    category = Column(String(64), index=True, default="Computer Science", nullable=False)
    difficulty = Column(String(32), default="Beginner", nullable=False)  # Beginner, Intermediate, Advanced
    duration_hours = Column(Integer, default=20, nullable=False)

    prerequisites = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True)
    syllabus_summary = Column(Text, nullable=True)

    # Instructor Association
    instructor_id = Column(Integer, ForeignKey("instructor_profiles.id", ondelete="SET NULL"), nullable=True)
    instructor = relationship("InstructorProfile", back_populates="courses", lazy="joined")

    # Workflow Status: 'draft', 'pending_approval', 'approved', 'published', 'archived'
    status = Column(String(32), default="draft", index=True, nullable=False)
    rejection_reason = Column(Text, nullable=True)

    # Academic Rules & Capacity
    capacity = Column(Integer, default=100, nullable=False)
    passing_grade = Column(Float, default=60.0, nullable=False)  # Minimum score % to pass
    is_certificate_enabled = Column(Boolean, default=True, nullable=False)
    thumbnail_url = Column(String(255), nullable=True)

    # Relationships
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan", order_by="CourseModule.order_index")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    attendance_sessions = relationship("AttendanceSession", back_populates="course", cascade="all, delete-orphan")
    discussions = relationship("DiscussionTopic", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")
    grading_scheme = relationship("GradingScheme", back_populates="course", uselist=False, cascade="all, delete-orphan")

    @property
    def active_enrollment_count(self) -> int:
        """Count of active enrolled students."""
        return sum(1 for e in self.enrollments if e.status == "active")

    @property
    def is_full(self) -> bool:
        """Check if course enrollment capacity has been reached."""
        if self.capacity <= 0:
            return False
        return self.active_enrollment_count >= self.capacity

    @property
    def is_published(self) -> bool:
        """Check if course is currently live and published."""
        return self.status == "published"

    def __repr__(self):
        return f"<Course {self.code}: {self.title} [{self.status}]>"
