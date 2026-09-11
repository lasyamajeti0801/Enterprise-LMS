"""Course Module services for managing curriculum structures."""

from core.database import get_session
from core.exceptions import ResourceNotFoundError
from modules.models import CourseModule


class ModuleService:
    """Operations for creating, updating, and reordering curriculum modules."""

    @staticmethod
    def create_module(course_id: int, title: str, description: str = "", order_index: int = None) -> CourseModule:
        """Add a new module to a course."""
        session = get_session()
        if order_index is None:
            max_idx = session.query(CourseModule).filter_by(course_id=course_id).count()
            order_index = max_idx + 1

        module = CourseModule(
            course_id=course_id,
            title=title.strip(),
            description=description.strip(),
            order_index=order_index,
            is_published=True,
        )
        session.add(module)
        session.commit()
        return module

    @staticmethod
    def get_by_id(module_id: int) -> CourseModule:
        """Fetch module by ID."""
        module = get_session().query(CourseModule).filter_by(id=module_id).first()
        if not module:
            raise ResourceNotFoundError(f"Module {module_id} not found.")
        return module

    @staticmethod
    def update_module(module_id: int, title: str = None, description: str = None, is_published: bool = None) -> CourseModule:
        """Update module properties."""
        session = get_session()
        module = ModuleService.get_by_id(module_id)
        if title is not None:
            module.title = title.strip()
        if description is not None:
            module.description = description.strip()
        if is_published is not None:
            module.is_published = is_published
        session.commit()
        return module

    @staticmethod
    def delete_module(module_id: int) -> bool:
        """Delete module and all associated child lessons."""
        session = get_session()
        module = ModuleService.get_by_id(module_id)
        session.delete(module)
        session.commit()
        return True
