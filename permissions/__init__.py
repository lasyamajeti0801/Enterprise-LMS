"""Permissions package initialization."""

from permissions.models import Permission
from permissions.services import PermissionService

__all__ = ["Permission", "PermissionService"]
