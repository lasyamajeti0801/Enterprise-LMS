"""Lesson model representing individual learning units, articles, videos, and study guides."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class Lesson(Base, ModelMixin):
    """Individual learning unit containing instructional content and resources."""

    __tablename__ = "lessons"

    module_id = Column(Integer, ForeignKey("course_modules.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    content_type = Column(String(32), default="text", nullable=False)  # 'text', 'video', 'interactive', 'pdf'
    content = Column(Text, nullable=False)  # Markdown or HTML lesson content
    summary = Column(String(500), nullable=True)

    order_index = Column(Integer, default=1, nullable=False)
    duration_minutes = Column(Integer, default=15, nullable=False)
    is_preview = Column(Boolean, default=False, nullable=False)  # Can be viewed before enrollment
    is_published = Column(Boolean, default=True, nullable=False)

    learning_objectives = Column(Text, nullable=True)
    exercise_prompt = Column(Text, nullable=True)

    # Relationships
    module = relationship("CourseModule", back_populates="lessons")
    materials = relationship("LessonMaterial", back_populates="lesson", cascade="all, delete-orphan")
    progress_records = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson {self.order_index}: {self.title}>"
