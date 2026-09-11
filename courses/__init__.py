"""Courses package initialization."""

from courses.models import Course, slugify
from courses.services import CourseService

__all__ = ["Course", "CourseService", "slugify"]
