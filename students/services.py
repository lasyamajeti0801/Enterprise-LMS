"""Student profile management services."""

import random
from core.database import get_session
from core.pagination import paginate_query
from students.models import StudentProfile
from users.models import User


class StudentService:
    """Operations related to student academic profiles and performance tracking."""

    @staticmethod
    def create_or_get_profile(user_id: int, major: str = "Computer Science", enrollment_year: int = 2026) -> StudentProfile:
        """Create or retrieve a student profile for a user."""
        session = get_session()
        profile = session.query(StudentProfile).filter_by(user_id=user_id).first()
        if not profile:
            student_num = f"STD-{enrollment_year}-{random.randint(10000, 99999)}"
            profile = StudentProfile(
                user_id=user_id,
                student_id_number=student_num,
                major=major,
                enrollment_year=enrollment_year,
                academic_standing="Good Standing",
                gpa=4.0,
                total_credits=0,
            )
            session.add(profile)
            session.commit()
        return profile

    @staticmethod
    def get_by_user_id(user_id: int) -> StudentProfile | None:
        """Fetch student profile by User ID."""
        return get_session().query(StudentProfile).filter_by(user_id=user_id).first()

    @staticmethod
    def get_all_students(page: int = 1, per_page: int = 15):
        """Retrieve paginated list of all registered students with user info."""
        query = get_session().query(StudentProfile).join(User).order_by(StudentProfile.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def update_gpa(student_profile_id: int, new_gpa: float):
        """Update student GPA."""
        session = get_session()
        profile = session.query(StudentProfile).filter_by(id=student_profile_id).first()
        if profile:
            profile.gpa = round(max(0.0, min(4.0, float(new_gpa))), 2)
            session.commit()
        return profile
