"""Permission services for granular permission checks."""

from core.database import get_session
from roles.models import Permission


class PermissionService:
    """Service to query, verify and manage permissions."""

    @staticmethod
    def get_by_code(code: str):
        return get_session().query(Permission).filter_by(code=code).first()

    @staticmethod
    def get_all():
        return get_session().query(Permission).order_by(Permission.module, Permission.name).all()
