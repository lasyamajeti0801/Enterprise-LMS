"""Lesson supplementary learning materials and attachments."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class LessonMaterial(Base, ModelMixin):
    """Supplementary learning asset (PDF, slide deck, sample code, cheatsheet)."""

    __tablename__ = "lesson_materials"

    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    material_type = Column(String(32), default="document", nullable=False)  # 'pdf', 'zip', 'code', 'link'
    file_path = Column(String(255), nullable=True)
    external_url = Column(String(500), nullable=True)
    file_size_kb = Column(Integer, default=0, nullable=False)

    lesson = relationship("Lesson", back_populates="materials")

    def __repr__(self):
        return f"<LessonMaterial {self.title} ({self.material_type})>"
