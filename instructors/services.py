"""Instructor management and approval services."""

import random
from core.database import get_session
from core.pagination import paginate_query
from instructors.models import InstructorProfile
from users.models import User


class InstructorService:
    """Operations related to instructor profiles, approvals, and metrics."""

    @staticmethod
    def create_or_get_profile(
        user_id: int,
        title: str = "Assistant Professor",
        department: str = "Computer Science",
        office_location: str = "Science Block B-302",
        qualifications: str = "Ph.D. in Computer Science",
        expertise_areas: str = "Distributed Systems, AI, Web Architecture",
        approval_status: str = "approved",
    ) -> InstructorProfile:
        """Create or retrieve instructor profile."""
        session = get_session()
        profile = session.query(InstructorProfile).filter_by(user_id=user_id).first()
        if not profile:
            emp_num = f"EMP-{random.randint(1000, 9999)}"
            profile = InstructorProfile(
                user_id=user_id,
                employee_id=emp_num,
                title=title,
                department=department,
                office_location=office_location,
                qualifications=qualifications,
                expertise_areas=expertise_areas,
                approval_status=approval_status,
                rating=4.9,
            )
            session.add(profile)
            session.commit()
        return profile

    @staticmethod
    def get_by_user_id(user_id: int) -> InstructorProfile | None:
        """Get instructor profile by user ID."""
        return get_session().query(InstructorProfile).filter_by(user_id=user_id).first()

    @staticmethod
    def get_all_instructors(status: str = "", page: int = 1, per_page: int = 15):
        """Retrieve paginated instructors."""
        query = get_session().query(InstructorProfile).join(User)
        if status:
            query = query.filter(InstructorProfile.approval_status == status.lower())
        query = query.order_by(InstructorProfile.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def set_approval_status(instructor_id: int, status: str) -> InstructorProfile:
        """Approve or reject instructor application."""
        session = get_session()
        profile = session.query(InstructorProfile).filter_by(id=instructor_id).first()
        if profile:
            profile.approval_status = status.lower()
            session.commit()
        return profile
