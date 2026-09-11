"""Skill taxonomy and competency tracking services."""

from core.database import get_session
from core.exceptions import ResourceNotFoundError
from skills.models import CourseSkill, Skill, StudentSkill


class SkillService:
    """Operations managing skills catalog, course mapping, and learner competencies."""

    @staticmethod
    def create_skill(name: str, category: str = "Technical", description: str = "", icon: str = "code") -> Skill:
        """Create or retrieve a skill."""
        session = get_session()
        skill = session.query(Skill).filter_by(name=name.strip()).first()
        if not skill:
            skill = Skill(
                name=name.strip(),
                category=category.strip(),
                description=description.strip() if description else None,
                icon=icon.strip(),
            )
            session.add(skill)
            session.commit()
        return skill

    @staticmethod
    def map_skill_to_course(course_id: int, skill_id: int, target_mastery: str = "Intermediate") -> CourseSkill:
        """Link a skill to a course curriculum."""
        session = get_session()
        mapping = (
            session.query(CourseSkill)
            .filter_by(course_id=course_id, skill_id=skill_id)
            .first()
        )
        if not mapping:
            mapping = CourseSkill(course_id=course_id, skill_id=skill_id, target_mastery=target_mastery)
            session.add(mapping)
            session.commit()
        return mapping

    @staticmethod
    def update_student_skill(student_id: int, skill_id: int, proficiency: float, is_verified: bool = False) -> StudentSkill:
        """Update or record student proficiency in a specific skill."""
        session = get_session()
        record = (
            session.query(StudentSkill)
            .filter_by(student_id=student_id, skill_id=skill_id)
            .first()
        )
        prof_val = round(max(0.0, min(100.0, float(proficiency))), 1)

        if not record:
            record = StudentSkill(
                student_id=student_id,
                skill_id=skill_id,
                proficiency_percentage=prof_val,
                is_verified=is_verified,
            )
            session.add(record)
        else:
            record.proficiency_percentage = max(record.proficiency_percentage, prof_val)
            if is_verified:
                record.is_verified = True

        session.commit()
        return record

    @staticmethod
    def get_student_skills(student_id: int) -> list[StudentSkill]:
        """Fetch all skills mastered or learned by a student."""
        return (
            get_session()
            .query(StudentSkill)
            .filter_by(student_id=student_id)
            .order_by(StudentSkill.proficiency_percentage.desc())
            .all()
        )

    @staticmethod
    def get_course_skills(course_id: int) -> list[Skill]:
        """Fetch all skills taught in a course."""
        mappings = get_session().query(CourseSkill).filter_by(course_id=course_id).all()
        return [m.skill for m in mappings if m.skill]
