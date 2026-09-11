"""Lesson services for content authoring, publishing, and materials attachment."""

from core.database import get_session
from core.exceptions import ResourceNotFoundError
from lessons.models import Lesson
from materials.models import LessonMaterial


class LessonService:
    """Operations for lesson management and resource attachments."""

    @staticmethod
    def create_lesson(
        module_id: int,
        title: str,
        content: str,
        content_type: str = "text",
        summary: str = "",
        duration_minutes: int = 15,
        is_preview: bool = False,
        learning_objectives: str = "",
        exercise_prompt: str = "",
        order_index: int = None,
    ) -> Lesson:
        """Create a new lesson inside a module."""
        session = get_session()
        if order_index is None:
            max_idx = session.query(Lesson).filter_by(module_id=module_id).count()
            order_index = max_idx + 1

        lesson = Lesson(
            module_id=module_id,
            title=title.strip(),
            content=content.strip(),
            content_type=content_type,
            summary=summary.strip(),
            duration_minutes=duration_minutes,
            is_preview=is_preview,
            learning_objectives=learning_objectives,
            exercise_prompt=exercise_prompt,
            order_index=order_index,
            is_published=True,
        )
        session.add(lesson)
        session.commit()
        return lesson

    @staticmethod
    def get_by_id(lesson_id: int) -> Lesson:
        """Retrieve lesson by ID."""
        lesson = get_session().query(Lesson).filter_by(id=lesson_id).first()
        if not lesson:
            raise ResourceNotFoundError(f"Lesson {lesson_id} not found.")
        return lesson

    @staticmethod
    def update_lesson(lesson_id: int, **kwargs) -> Lesson:
        """Update lesson content and configuration."""
        session = get_session()
        lesson = LessonService.get_by_id(lesson_id)

        allowed = {
            "title", "content", "content_type", "summary", "duration_minutes",
            "is_preview", "is_published", "learning_objectives", "exercise_prompt", "order_index"
        }
        for field, value in kwargs.items():
            if field in allowed and value is not None:
                setattr(lesson, field, value)

        session.commit()
        return lesson

    @staticmethod
    def add_material(
        lesson_id: int,
        title: str,
        material_type: str = "document",
        file_path: str = None,
        external_url: str = None,
        file_size_kb: int = 0,
    ) -> LessonMaterial:
        """Attach a study material to a lesson."""
        session = get_session()
        material = LessonMaterial(
            lesson_id=lesson_id,
            title=title.strip(),
            material_type=material_type,
            file_path=file_path,
            external_url=external_url,
            file_size_kb=file_size_kb,
        )
        session.add(material)
        session.commit()
        return material

    @staticmethod
    def delete_lesson(lesson_id: int) -> bool:
        """Delete lesson."""
        session = get_session()
        lesson = LessonService.get_by_id(lesson_id)
        session.delete(lesson)
        session.commit()
        return True
