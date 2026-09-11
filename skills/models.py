"""Skill taxonomy and student competency mastery models."""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin


class Skill(Base, ModelMixin):
    """Core skill competency (e.g. Python Programming, Database Design, REST APIs)."""

    __tablename__ = "skills"

    name = Column(String(128), unique=True, nullable=False)
    category = Column(String(64), default="Technical", nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(64), default="code", nullable=False)

    course_mappings = relationship("CourseSkill", back_populates="skill", cascade="all, delete-orphan")
    student_masteries = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"


class CourseSkill(Base, ModelMixin):
    """Skills taught and developed within a course."""

    __tablename__ = "course_skills"
    __table_args__ = (UniqueConstraint("course_id", "skill_id", name="uq_course_skill"),)

    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    target_mastery = Column(String(32), default="Intermediate", nullable=False)

    skill = relationship("Skill", back_populates="course_mappings")
    course = relationship("Course")

    def __repr__(self):
        return f"<CourseSkill Course:{self.course_id} Skill:{self.skill_id}>"


class StudentSkill(Base, ModelMixin):
    """Student acquired skill proficiency percentage."""

    __tablename__ = "student_skills"
    __table_args__ = (UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),)

    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)

    proficiency_percentage = Column(Float, default=0.0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    skill = relationship("Skill", back_populates="student_masteries")
    student = relationship("StudentProfile")

    def __repr__(self):
        return f"<StudentSkill Student:{self.student_id} Skill:{self.skill_id} Prof:{self.proficiency_percentage}%>"
