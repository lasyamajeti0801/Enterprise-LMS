"""Discussion forum services for topics, threaded responses, and instructor badges."""

from core.database import get_session
from core.exceptions import ResourceNotFoundError
from core.pagination import paginate_query
from discussions.models import DiscussionReply, DiscussionTopic


class DiscussionService:
    """Operations managing course forum conversations and moderation."""

    @staticmethod
    def create_topic(course_id: int, user_id: int, title: str, content: str) -> DiscussionTopic:
        """Post a new discussion topic in a course forum."""
        session = get_session()
        topic = DiscussionTopic(
            course_id=course_id,
            user_id=user_id,
            title=title.strip(),
            content=content.strip(),
        )
        session.add(topic)
        session.commit()
        return topic

    @staticmethod
    def get_by_id(topic_id: int) -> DiscussionTopic:
        """Fetch discussion topic by ID and increment view count."""
        session = get_session()
        topic = session.query(DiscussionTopic).filter_by(id=topic_id).first()
        if not topic:
            raise ResourceNotFoundError(f"Topic {topic_id} not found.")
        topic.view_count += 1
        session.commit()
        return topic

    @staticmethod
    def add_reply(
        topic_id: int,
        user_id: int,
        content: str,
        parent_reply_id: int = None,
        is_instructor_answer: bool = False,
    ) -> DiscussionReply:
        """Post a reply to a discussion topic."""
        session = get_session()
        reply = DiscussionReply(
            topic_id=topic_id,
            user_id=user_id,
            content=content.strip(),
            parent_reply_id=parent_reply_id,
            is_instructor_answer=is_instructor_answer,
        )
        session.add(reply)
        session.commit()
        return reply

    @staticmethod
    def upvote_reply(reply_id: int) -> int:
        """Upvote a helpful reply."""
        session = get_session()
        reply = session.query(DiscussionReply).filter_by(id=reply_id).first()
        if reply:
            reply.upvotes += 1
            session.commit()
            return reply.upvotes
        return 0

    @staticmethod
    def get_course_topics(course_id: int, page: int = 1, per_page: int = 15):
        """Fetch paginated topics for a course forum."""
        query = (
            get_session()
            .query(DiscussionTopic)
            .filter_by(course_id=course_id)
            .order_by(DiscussionTopic.is_pinned.desc(), DiscussionTopic.id.desc())
        )
        return paginate_query(query, page=page, per_page=per_page)
