"""In-app notifications delivery and unread count services."""

from core.database import get_session
from core.events import events
from core.pagination import paginate_query
from notifications.models import Notification
from students.models import StudentProfile


class NotificationService:
    """Operations managing in-app notifications and alerts."""

    @staticmethod
    def send_notification(
        user_id: int,
        title: str,
        message: str,
        category: str = "System",
        action_url: str = None,
    ) -> Notification:
        """Deliver an internal notification to a user."""
        session = get_session()
        notification = Notification(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            category=category,
            action_url=action_url,
            is_read=False,
        )
        session.add(notification)
        session.commit()
        return notification

    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, page: int = 1, per_page: int = 15):
        """Retrieve paginated notifications for a user."""
        query = get_session().query(Notification).filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        query = query.order_by(Notification.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Count unread notifications for navigation badge."""
        return (
            get_session()
            .query(Notification)
            .filter_by(user_id=user_id, is_read=False)
            .count()
        )

    @staticmethod
    def mark_all_as_read(user_id: int):
        """Mark all notifications as read for a user."""
        session = get_session()
        session.query(Notification).filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        session.commit()


# Event handlers for automated system notifications
def _on_assignment_graded(student_id, assignment_id, score):
    student = get_session().query(StudentProfile).filter_by(id=student_id).first()
    if student:
        NotificationService.send_notification(
            user_id=student.user_id,
            title="Assignment Graded",
            message=f"Your assignment submission has been evaluated. Score: {score}",
            category="Grade",
        )

events.subscribe("assignment_graded", _on_assignment_graded)
