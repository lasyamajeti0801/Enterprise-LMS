"""Unified search engine across courses, lessons, users, and discussion forums."""

from sqlalchemy import or_
from core.database import get_session
from courses.models import Course
from discussions.models import DiscussionTopic
from lessons.models import Lesson
from users.models import User


class SearchService:
    """Operations executing multi-entity full-text queries."""

    @staticmethod
    def global_search(query_str: str, limit: int = 20) -> dict[str, list]:
        """Search across courses, lessons, users, and discussions simultaneously."""
        if not query_str or len(query_str.strip()) < 2:
            return {"courses": [], "lessons": [], "users": [], "discussions": []}

        session = get_session()
        term = f"%{query_str.strip()}%"

        courses = (
            session.query(Course)
            .filter(
                Course.status == "published",
                or_(
                    Course.title.ilike(term),
                    Course.code.ilike(term),
                    Course.short_description.ilike(term),
                    Course.category.ilike(term),
                ),
            )
            .limit(limit)
            .all()
        )

        lessons = (
            session.query(Lesson)
            .filter(
                Lesson.is_published == True,
                or_(
                    Lesson.title.ilike(term),
                    Lesson.summary.ilike(term),
                    Lesson.content.ilike(term),
                ),
            )
            .limit(limit)
            .all()
        )

        users = (
            session.query(User)
            .filter(
                User.status == "active",
                or_(
                    User.username.ilike(term),
                    User.email.ilike(term),
                    User.first_name.ilike(term),
                    User.last_name.ilike(term),
                ),
            )
            .limit(limit)
            .all()
        )

        discussions = (
            session.query(DiscussionTopic)
            .filter(
                or_(
                    DiscussionTopic.title.ilike(term),
                    DiscussionTopic.content.ilike(term),
                )
            )
            .limit(limit)
            .all()
        )

        return {
            "courses": courses,
            "lessons": lessons,
            "users": users,
            "discussions": discussions,
        }
