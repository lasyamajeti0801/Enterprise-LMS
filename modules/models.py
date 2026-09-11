"""Course Module model representing structured units within a curriculum."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class CourseModule(Base, ModelMixin):
    """Module grouping a sequence of lessons, exercises, and assessments."""

    __tablename__ = "course_modules"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=1, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")
    quizzes = relationship("Quiz", back_populates="module", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CourseModule {self.order_index}: {self.title}>"
