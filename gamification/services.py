"""Gamification service managing XP awards, badge grants, streaks, and leaderboards."""

from datetime import date, timedelta
from core.database import get_session, get_utc_now
from core.events import events
from gamification.models import Badge, UserBadge, UserPoints
from students.models import StudentProfile
from users.models import User

DEFAULT_BADGES = [
    ("first_lesson", "First Step", "Completed your very first lesson.", "book-open", 50),
    ("quiz_ace", "Quiz Ace", "Achieved 100% on a course quiz.", "zap", 100),
    ("course_champ", "Course Champion", "Completed an entire accredited course.", "award", 250),
    ("perfect_attendance", "Always Present", "Maintained 100% course attendance.", "calendar-check", 150),
    ("streak_7", "7-Day Scholar", "Studied 7 days consecutively.", "flame", 200),
    ("speed_learner", "Speed Learner", "Completed 5 lessons in a single day.", "trending-up", 120),
]


class GamificationService:
    """Operations managing learner rewards, XP levels, badges, and streaks."""

    @staticmethod
    def seed_default_badges():
        """Ensure standard badges exist in database."""
        session = get_session()
        for code, name, desc, icon, reward in DEFAULT_BADGES:
            badge = session.query(Badge).filter_by(code=code).first()
            if not badge:
                badge = Badge(code=code, name=name, description=desc, icon_name=icon, xp_reward=reward)
                session.add(badge)
        session.commit()

    @staticmethod
    def get_or_create_user_points(user_id: int) -> UserPoints:
        """Fetch or initialize UserPoints record."""
        session = get_session()
        points = session.query(UserPoints).filter_by(user_id=user_id).first()
        if not points:
            points = UserPoints(
                user_id=user_id,
                total_xp=0,
                current_level=1,
                current_streak_days=1,
                last_activity_date=date.today(),
            )
            session.add(points)
            session.commit()
        return points

    @staticmethod
    def award_xp(user_id: int, xp_amount: int, update_streak: bool = True) -> UserPoints:
        """Award experience points and adjust player level."""
        session = get_session()
        points = GamificationService.get_or_create_user_points(user_id)

        points.total_xp += max(0, int(xp_amount))
        # Calculate level: every 250 XP is a new level
        points.current_level = (points.total_xp // 250) + 1

        if update_streak:
            today = date.today()
            if points.last_activity_date:
                if points.last_activity_date == today - timedelta(days=1):
                    points.current_streak_days += 1
                elif points.last_activity_date < today - timedelta(days=1):
                    points.current_streak_days = 1
            points.last_activity_date = today

        session.commit()
        return points

    @staticmethod
    def award_badge(user_id: int, badge_code: str) -> bool:
        """Award an achievement badge to a user if not already earned."""
        session = get_session()
        badge = session.query(Badge).filter_by(code=badge_code).first()
        if not badge:
            return False

        existing = (
            session.query(UserBadge)
            .filter_by(user_id=user_id, badge_id=badge.id)
            .first()
        )
        if existing:
            return False  # Already earned

        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge.id,
            awarded_at=get_utc_now(),
        )
        session.add(user_badge)
        session.commit()

        # Also award bonus XP
        GamificationService.award_xp(user_id, badge.xp_reward, update_streak=False)
        return True

    @staticmethod
    def get_leaderboard(limit: int = 10) -> list[dict]:
        """Fetch platform top learners ranked by total XP."""
        session = get_session()
        results = (
            session.query(UserPoints)
            .join(User)
            .order_by(UserPoints.total_xp.desc())
            .limit(limit)
            .all()
        )
        leaderboard = []
        for rank, p in enumerate(results, start=1):
            leaderboard.append({
                "rank": rank,
                "user_id": p.user_id,
                "full_name": p.user.full_name if p.user else "Anonymous Learner",
                "username": p.user.username if p.user else "learner",
                "total_xp": p.total_xp,
                "level": p.current_level,
                "streak": p.current_streak_days,
            })
        return leaderboard

    @staticmethod
    def get_user_badges(user_id: int) -> list[Badge]:
        """Retrieve list of all badges earned by user."""
        session = get_session()
        records = (
            session.query(UserBadge)
            .filter_by(user_id=user_id)
            .order_by(UserBadge.awarded_at.desc())
            .all()
        )
        return [r.badge for r in records if r.badge]


# Wire domain events into gamification triggers
def _on_lesson_completed(student_id, lesson_id, course_id):
    student = get_session().query(StudentProfile).filter_by(id=student_id).first()
    if student:
        GamificationService.award_xp(student.user_id, 50)
        GamificationService.award_badge(student.user_id, "first_lesson")

def _on_quiz_passed(student_id, quiz_id, percentage):
    student = get_session().query(StudentProfile).filter_by(id=student_id).first()
    if student:
        GamificationService.award_xp(student.user_id, 100)
        if percentage >= 100.0:
            GamificationService.award_badge(student.user_id, "quiz_ace")

def _on_course_completed(student_id, course_id):
    student = get_session().query(StudentProfile).filter_by(id=student_id).first()
    if student:
        GamificationService.award_xp(student.user_id, 500)
        GamificationService.award_badge(student.user_id, "course_champ")

events.subscribe("lesson_completed", _on_lesson_completed)
events.subscribe("quiz_passed", _on_quiz_passed)
events.subscribe("course_completed", _on_course_completed)
