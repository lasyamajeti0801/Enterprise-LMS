"""Assignments package initialization."""

from assignments.models import Assignment
from assignments.services import AssignmentService

__all__ = ["Assignment", "AssignmentService"]
