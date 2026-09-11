"""Calendar and timetable scheduling services."""

from datetime import datetime, timedelta
from sqlalchemy import or_
from core.database import get_session
from calendar_events.models import CalendarEvent


class CalendarService:
    """Operations managing academic schedules, exam dates, assignment deadlines, and personal agendas."""

    @staticmethod
    def create_event(
        title: str,
        start_time: datetime,
        end_time: datetime,
        event_type: str = "Class",
        course_id: int = None,
        user_id: int = None,
        description: str = "",
        location_or_link: str = "",
    ) -> CalendarEvent:
        """Create a scheduled event."""
        session = get_session()
        event = CalendarEvent(
            title=title.strip(),
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            course_id=course_id,
            user_id=user_id,
            description=description.strip() if description else None,
            location_or_link=location_or_link.strip() if location_or_link else None,
        )
        session.add(event)
        session.commit()
        return event

    @staticmethod
    def get_upcoming_events(course_ids: list[int] = None, user_id: int = None, days_ahead: int = 30) -> list[CalendarEvent]:
        """Fetch chronological upcoming events within the window."""
        session = get_session()
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        query = session.query(CalendarEvent).filter(CalendarEvent.start_time >= now, CalendarEvent.start_time <= future)

        filters = []
        if course_ids:
            filters.append(CalendarEvent.course_id.in_(course_ids))
        if user_id:
            filters.append(CalendarEvent.user_id == user_id)

        if filters:
            query = query.filter(or_(*filters))

        return query.order_by(CalendarEvent.start_time.asc()).all()
