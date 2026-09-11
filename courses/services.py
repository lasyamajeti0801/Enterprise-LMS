"""Course management service with approval workflows, publishing, and filtering."""

from sqlalchemy import or_
from core.database import get_session
from core.exceptions import CourseNotFoundError, PermissionDeniedError, ValidationError
from core.pagination import paginate_query
from courses.models import Course, slugify
from instructors.models import InstructorProfile


class CourseService:
    """Enterprise course lifecycle and curriculum operations."""

    @staticmethod
    def create_course(
        code: str,
        title: str,
        short_description: str,
        full_description: str,
        instructor_id: int | None = None,
        category: str = "Computer Science",
        difficulty: str = "Beginner",
        duration_hours: int = 20,
        prerequisites: str = "",
        learning_objectives: str = "",
        syllabus_summary: str = "",
        capacity: int = 100,
        passing_grade: float = 60.0,
        status: str = "draft",
    ) -> Course:
        """Create a new course."""
        session = get_session()
        code = code.strip().upper()
        title = title.strip()

        if session.query(Course).filter_by(code=code).first():
            raise ValidationError(f"Course with code '{code}' already exists.")

        base_slug = slugify(title)
        slug = base_slug
        count = 1
        while session.query(Course).filter_by(slug=slug).first():
            slug = f"{base_slug}-{count}"
            count += 1

        course = Course(
            code=code,
            title=title,
            slug=slug,
            short_description=short_description.strip(),
            full_description=full_description.strip(),
            instructor_id=instructor_id,
            category=category,
            difficulty=difficulty,
            duration_hours=duration_hours,
            prerequisites=prerequisites,
            learning_objectives=learning_objectives,
            syllabus_summary=syllabus_summary,
            capacity=capacity,
            passing_grade=passing_grade,
            status=status,
        )
        session.add(course)
        session.commit()
        return course

    @staticmethod
    def get_by_id(course_id: int) -> Course:
        """Fetch course by ID or raise CourseNotFoundError."""
        course = get_session().query(Course).filter_by(id=course_id).first()
        if not course:
            raise CourseNotFoundError(course_id)
        return course

    @staticmethod
    def get_by_slug(slug: str) -> Course:
        """Fetch course by slug or raise CourseNotFoundError."""
        course = get_session().query(Course).filter_by(slug=slug).first()
        if not course:
            raise CourseNotFoundError(slug)
        return course

    @staticmethod
    def update_course(course_id: int, **kwargs) -> Course:
        """Update course metadata and settings."""
        session = get_session()
        course = CourseService.get_by_id(course_id)

        allowed_fields = {
            "title", "short_description", "full_description", "category", "difficulty",
            "duration_hours", "prerequisites", "learning_objectives", "syllabus_summary",
            "capacity", "passing_grade", "is_certificate_enabled", "thumbnail_url",
            "instructor_id", "status", "rejection_reason"
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(course, field, value)

        if "title" in kwargs and kwargs["title"]:
            base_slug = slugify(kwargs["title"])
            slug = base_slug
            count = 1
            while session.query(Course).filter(Course.slug == slug, Course.id != course_id).first():
                slug = f"{base_slug}-{count}"
                count += 1
            course.slug = slug

        session.commit()
        return course

    @staticmethod
    def submit_for_approval(course_id: int) -> Course:
        """Submit draft course for Administrator approval."""
        return CourseService.update_course(course_id, status="pending_approval")

    @staticmethod
    def approve_course(course_id: int) -> Course:
        """Administrator approves course."""
        return CourseService.update_course(course_id, status="approved", rejection_reason=None)

    @staticmethod
    def reject_course(course_id: int, reason: str) -> Course:
        """Administrator rejects course with explanation."""
        return CourseService.update_course(course_id, status="draft", rejection_reason=reason)

    @staticmethod
    def publish_course(course_id: int) -> Course:
        """Publish approved course to public catalog."""
        course = CourseService.get_by_id(course_id)
        if course.status not in ("approved", "published"):
            raise ValidationError("Only approved courses can be published.")
        course.status = "published"
        get_session().commit()
        return course

    @staticmethod
    def archive_course(course_id: int) -> Course:
        """Archive course."""
        return CourseService.update_course(course_id, status="archived")

    @staticmethod
    def list_published_courses(category: str = "", difficulty: str = "", query_str: str = "", page: int = 1, per_page: int = 12):
        """List publicly available published courses."""
        query = get_session().query(Course).filter(Course.status == "published")

        if category:
            query = query.filter(Course.category == category)
        if difficulty:
            query = query.filter(Course.difficulty == difficulty)
        if query_str:
            term = f"%{query_str.strip()}%"
            query = query.filter(or_(Course.title.ilike(term), Course.short_description.ilike(term), Course.code.ilike(term)))

        query = query.order_by(Course.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def list_instructor_courses(instructor_id: int, status: str = "", page: int = 1, per_page: int = 15):
        """List courses owned by a specific instructor."""
        query = get_session().query(Course).filter(Course.instructor_id == instructor_id)
        if status:
            query = query.filter(Course.status == status)
        query = query.order_by(Course.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def list_all_courses(status: str = "", query_str: str = "", page: int = 1, per_page: int = 15):
        """Administrator query across all courses."""
        query = get_session().query(Course)
        if status:
            query = query.filter(Course.status == status)
        if query_str:
            term = f"%{query_str.strip()}%"
            query = query.filter(or_(Course.title.ilike(term), Course.code.ilike(term)))
        query = query.order_by(Course.id.desc())
        return paginate_query(query, page=page, per_page=per_page)
