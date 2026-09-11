"""Course discussion forum and threaded reply models."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class DiscussionTopic(Base, ModelMixin):
    """Discussion thread initiated within a course forum."""

    __tablename__ = "discussion_topics"

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="discussions")
    author = relationship("User")
    replies = relationship("DiscussionReply", back_populates="topic", cascade="all, delete-orphan", order_by="DiscussionReply.created_at")

    @property
    def reply_count(self) -> int:
        return len(self.replies)

    def __repr__(self):
        return f"<DiscussionTopic {self.id}: {self.title}>"


class DiscussionReply(Base, ModelMixin):
    """Threaded reply to a course discussion topic."""

    __tablename__ = "discussion_replies"

    topic_id = Column(Integer, ForeignKey("discussion_topics.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    parent_reply_id = Column(Integer, ForeignKey("discussion_replies.id", ondelete="CASCADE"), nullable=True)

    content = Column(Text, nullable=False)
    is_instructor_answer = Column(Boolean, default=False, nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)

    topic = relationship("DiscussionTopic", back_populates="replies")
    author = relationship("User")

    def __repr__(self):
        return f"<DiscussionReply {self.id} on Topic:{self.topic_id}>"
