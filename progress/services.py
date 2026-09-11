"""Learning progress calculation and state management engine."""

from core.database import get_session, get_utc_now
from core.events import events
from courses.models import Course
from enrollment.models import CourseEnrollment
from lessons.models import Lesson
from modules.models import CourseModule
from progress.models import LessonProgress


class ProgressService:
    """Operations calculating hierarchical lesson, module, and course completion."""

    @staticmethod
    def mark_lesson_completed(enrollment_id: int, lesson_id: int, time_spent_seconds: int = 60) -> dict:
        """Mark a lesson as completed by an enrolled student and recalculate course progress."""
        session = get_session()

        enrollment = session.query(CourseEnrollment).filter_by(id=enrollment_id).first()
        if not enrollment:
            return {"success": False, "error": "Enrollment not found"}

        progress_record = (
            session.query(LessonProgress)
            .filter_by(enrollment_id=enrollment.id, lesson_id=lesson_id)
            .first()
        )

        was_already_completed = progress_record and progress_record.is_completed

        if not progress_record:
            progress_record = LessonProgress(
                enrollment_id=enrollment.id,
                student_id=enrollment.student_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=get_utc_now(),
                time_spent_seconds=time_spent_seconds,
            )
            session.add(progress_record)
        else:
            progress_record.is_completed = True
            progress_record.completed_at = get_utc_now()
            progress_record.time_spent_seconds += time_spent_seconds

        session.commit()

        # Recalculate total course progress
        new_progress = ProgressService.calculate_course_progress(enrollment.id)

        # Trigger Gamification Event if newly completed
        if not was_already_completed:
            events.emit(
                "lesson_completed",
                student_id=enrollment.student_id,
                lesson_id=lesson_id,
                course_id=enrollment.course_id,
            )

        if new_progress >= 100.0 and enrollment.status == "active":
            enrollment.status = "completed"
            enrollment.completion_date = get_utc_now()
            session.commit()
            events.emit(
                "course_completed",
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
            )

        return {
            "success": True,
            "is_completed": True,
            "course_progress": new_progress,
            "status": enrollment.status,
        }

    @staticmethod
    def calculate_course_progress(enrollment_id: int) -> float:
        """Calculate exact completion percentage across all lessons in course."""
        session = get_session()
        enrollment = session.query(CourseEnrollment).filter_by(id=enrollment_id).first()
        if not enrollment:
            return 0.0

        # Total published lessons in course
        all_lessons = (
            session.query(Lesson)
            .join(CourseModule)
            .filter(CourseModule.course_id == enrollment.course_id, Lesson.is_published == True)
            .all()
        )

        total_lessons = len(all_lessons)
        if total_lessons == 0:
            enrollment.progress_percentage = 100.0
            session.commit()
            return 100.0

        lesson_ids = [l.id for l in all_lessons]
        completed_count = (
            session.query(LessonProgress)
            .filter(
                LessonProgress.enrollment_id == enrollment.id,
                LessonProgress.lesson_id.in_(lesson_ids),
                LessonProgress.is_completed == True,
            )
            .count()
        )

        progress = round((completed_count / total_lessons) * 100.0, 1)
        enrollment.progress_percentage = progress
        session.commit()
        return progress

    @staticmethod
    def get_completed_lesson_ids(enrollment_id: int) -> set[int]:
        """Return set of completed lesson IDs for an enrollment."""
        records = (
            get_session()
            .query(LessonProgress.lesson_id)
            .filter_by(enrollment_id=enrollment_id, is_completed=True)
            .all()
        )
        return {r[0] for r in records}
