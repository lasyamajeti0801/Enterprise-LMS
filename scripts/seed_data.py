"""Enterprise LMS - Seed Data Generator.

Populates realistic institutional data:
- Administrator, Instructors, and Students accounts
- Courses across multiple disciplines (CS, AI, Security, Web)
- Hierarchical curriculum: Modules, Lessons, Notes, Study Materials
- Question Bank, Quizzes, Assignments, Submissions, Grades
- Attendance Sessions and Student Attendance records
- Badges, Points, Streaks, Discussions, Calendar events, and Notifications
"""

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from assignments.services import AssignmentService
from attendance.services import AttendanceService
from calendar_events.services import CalendarService
from certificates.services import CertificateService
from core.database import get_session, init_db
from courses.models import Course
from courses.services import CourseService
from discussions.services import DiscussionService
from enrollment.services import EnrollmentService
from gamification.services import GamificationService
from grading.services import GradingService
from instructors.services import InstructorService
from lessons.services import LessonService
from modules.services import ModuleService
from notifications.services import NotificationService
from progress.services import ProgressService
from question_bank.services import QuestionBankService
from quizzes.services import QuizService
from roles.services import RoleService
from settings.services import SettingService
from skills.services import SkillService
from students.services import StudentService
from users.services import UserService


def run_seed(reset=False):
    """Execute full enterprise seed population."""
    app = create_app(config_name="development")
    with app.app_context():
        print("[SEED] Initializing database schema...")
        init_db()

        if reset:
            print("[SEED] Reset requested. Dropping all existing tables...")
            from core.database import Base, _engine
            Base.metadata.drop_all(bind=_engine)
            Base.metadata.create_all(bind=_engine)
            print("[SEED] Database schema reset successfully.")

        session = get_session()

        existing_courses = session.query(Course).count()
        if not reset and existing_courses > 0:
            print(f"[SEED] Database already contains {existing_courses} course(s). Seed data already present.")
            print("[SEED] Run 'python manage.py seed --reset' if you wish to wipe and re-seed from scratch.")
            return

        print("[SEED] Seeding roles, permissions, settings & badges...")
        RoleService.seed_default_roles_and_permissions()
        SettingService.seed_default_settings()
        GamificationService.seed_default_badges()

        # -------------------------------------------------------------
        # 1. USERS: Admin, Instructors, Students
        # -------------------------------------------------------------
        print("[SEED] Creating user accounts...")
        # Admin
        admin_user = UserService.get_by_identifier("admin")
        if not admin_user:
            admin_user = UserService.create_user(
                username="admin",
                email="admin@lms.local",
                password="adminpassword123",
                first_name="System",
                last_name="Administrator",
                role_name="admin",
            )

        # Instructors
        instructor_specs = [
            ("dr_hopper", "hopper@lms.local", "Grace", "Hopper", "Distinguished Professor", "Computer Science", "Ph.D. in Mathematics & Computing", "Compilers, Systems, Software Architecture"),
            ("dr_torvalds", "torvalds@lms.local", "Linus", "Torvalds", "Lead Research Professor", "Operating Systems", "M.S. in Computer Science", "Kernel Architecture, Git, C & Python"),
            ("prof_smith", "smith@lms.local", "Alan", "Smith", "Associate Professor", "Data Science & AI", "Ph.D. in Machine Learning", "Deep Learning, Algorithms, Python"),
        ]

        instructors = []
        for uname, email, fname, lname, title, dept, qual, exp in instructor_specs:
            user = UserService.get_by_identifier(uname)
            if not user:
                user = UserService.create_user(
                    username=uname,
                    email=email,
                    password="instructorpassword123",
                    first_name=fname,
                    last_name=lname,
                    role_name="instructor",
                )
                inst_prof = InstructorService.create_or_get_profile(
                    user_id=user.id,
                    title=title,
                    department=dept,
                    qualifications=qual,
                    expertise_areas=exp,
                    approval_status="approved",
                )
            else:
                inst_prof = InstructorService.get_by_user_id(user.id)
            instructors.append(inst_prof)

        # Students
        student_specs = [
            ("student_alex", "alex@student.lms.local", "Alex", "Rivera", "Computer Science", 2026),
            ("student_sarah", "sarah@student.lms.local", "Sarah", "Connor", "Software Engineering", 2026),
            ("student_david", "david@student.lms.local", "David", "Kim", "Artificial Intelligence", 2025),
            ("student_maya", "maya@student.lms.local", "Maya", "Patel", "Data Science", 2026),
            ("student_elena", "elena@student.lms.local", "Elena", "Rostova", "Cybersecurity", 2025),
        ]

        students = []
        for uname, email, fname, lname, major, year in student_specs:
            user = UserService.get_by_identifier(uname)
            if not user:
                user = UserService.create_user(
                    username=uname,
                    email=email,
                    password="studentpassword123",
                    first_name=fname,
                    last_name=lname,
                    role_name="student",
                )
                std_prof = StudentService.create_or_get_profile(
                    user_id=user.id,
                    major=major,
                    enrollment_year=year,
                )
            else:
                std_prof = StudentService.get_by_user_id(user.id)
            students.append(std_prof)

        # -------------------------------------------------------------
        # 2. COURSES & CURRICULUM
        # -------------------------------------------------------------
        print("[SEED] Creating courses and hierarchical curriculum...")
        course_specs = [
            (
                "CS-101",
                "Python Software Architecture & Design Patterns",
                "Master object-oriented programming, clean code principles, and scalable system design with Python.",
                "Comprehensive enterprise curriculum covering solid design patterns, domain-driven design, data modeling, automated testing, and high-performance backend development in Python.",
                instructors[0].id,
                "Computer Science",
                "Intermediate",
                30,
                [
                    ("Module 1: Foundations of Enterprise Python", [
                        ("Python 3.12 Core Features & Type Hinting", "Deep dive into static typing, generics, protocol classes, and modern Python features."),
                        ("Object-Oriented Design & SOLID Principles", "Applying Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion."),
                        ("Memory Management & Performance Profiling", "Understanding reference counting, garbage collection cycles, and optimizing execution bottlenecks."),
                    ]),
                    ("Module 2: Architectural Patterns & Clean Code", [
                        ("Domain-Driven Design (DDD) Bounded Contexts", "Modeling rich domain entities, value objects, domain services, and repository layers."),
                        ("Service Layer & Dependency Injection", "Decoupling business logic from framework routers and storage drivers."),
                    ]),
                ],
            ),
            (
                "AI-301",
                "Applied Machine Learning & Neural Networks",
                "Learn statistical learning, feature engineering, transformer architectures, and model evaluation.",
                "In-depth course on data preprocessing, regression, classification, unsupervised clustering, deep learning with PyTorch, and deploying local inference microservices.",
                instructors[2].id,
                "Data Science",
                "Advanced",
                40,
                [
                    ("Module 1: Mathematics of Machine Learning", [
                        ("Linear Algebra & Vector Spaces", "Vectors, matrices, eigenvalues, and dot products in computational learning."),
                        ("Gradient Descent & Convex Optimization", "Stochastic gradient descent, learning rate schedules, and convergence."),
                    ]),
                    ("Module 2: Neural Network Architectures", [
                        ("Feedforward Multi-Layer Perceptrons", "Backpropagation, activation functions, and vanishing gradient mitigation."),
                        ("Convolutional & Recurrent Networks", "Feature maps, spatial hierarchies, and sequence modeling."),
                    ]),
                ],
            ),
            (
                "SEC-201",
                "Enterprise Security & Cryptographic Systems",
                "Hands-on security engineering, PBKDF2 hashing, OAuth2, RBAC, and secure system hardening.",
                "Practical guide to defending modern web applications against OWASP Top 10 vulnerabilities, implementing cryptographic verification, and auditing access logs.",
                instructors[1].id,
                "Cybersecurity",
                "Intermediate",
                25,
                [
                    ("Module 1: Authentication & Access Control", [
                        ("Cryptographic Hashing & Salt Management", "PBKDF2, Argon2, and collision-resistant hash constructions."),
                        ("Role-Based Access Control (RBAC) Matrices", "Designing zero-trust role-permission hierarchies."),
                    ]),
                ],
            ),
        ]

        created_courses = []
        for code, title, sdesc, fdesc, inst_id, cat, diff, dur, modules in course_specs:
            course = CourseService.create_course(
                code=code,
                title=title,
                short_description=sdesc,
                full_description=fdesc,
                instructor_id=inst_id,
                category=cat,
                difficulty=diff,
                duration_hours=dur,
                status="published",
            )
            created_courses.append(course)

            # Build modules and lessons
            for mod_title, lessons in modules:
                module = ModuleService.create_module(course_id=course.id, title=mod_title)
                for l_title, l_summary in lessons:
                    lesson = LessonService.create_lesson(
                        module_id=module.id,
                        title=l_title,
                        summary=l_summary,
                        content=f"""# {l_title}

## Overview
{l_summary}

### Theoretical Principles
In enterprise software systems, structured modularity ensures that components are independently testable, maintainable, and extensible over decades of production operation.

```python
# Sample Implementation Pattern
class DomainEntity:
    def __init__(self, entity_id: int, name: str):
        self.entity_id = entity_id
        self.name = name

    def validate(self) -> bool:
        return bool(self.name and len(self.name) > 2)
```

### Key Takeaways
1. Always decouple data representation from persistence mechanisms.
2. Write unit tests for all domain invariants before deploying to production.
3. Maintain immutable audit trails for critical operations.
""",
                        duration_minutes=20,
                    )
                    LessonService.add_material(
                        lesson_id=lesson.id,
                        title=f"{l_title} - Official Study Guide",
                        material_type="document",
                    )

        # -------------------------------------------------------------
        # 3. QUESTION BANK & QUIZZES
        # -------------------------------------------------------------
        print("[SEED] Seeding question bank and course quizzes...")
        q1 = QuestionBankService.create_question(
            prompt="Which SOLID principle states that high-level modules should not depend on low-level modules, but both should depend on abstractions?",
            question_type="mcq_single",
            options=[
                "Dependency Inversion Principle (DIP)",
                "Single Responsibility Principle (SRP)",
                "Liskov Substitution Principle (LSP)",
                "Open-Closed Principle (OCP)",
            ],
            correct_answers=["Dependency Inversion Principle (DIP)"],
            category_name="Software Architecture",
            explanation="The Dependency Inversion Principle decouples software modules using abstract interfaces.",
            marks=5.0,
        )

        q2 = QuestionBankService.create_question(
            prompt="True or False: In Python, strings and tuples are mutable data types.",
            question_type="mcq_single",
            options=["True", "False"],
            correct_answers=["False"],
            category_name="Python Core",
            explanation="Strings and tuples in Python are immutable; lists and dictionaries are mutable.",
            marks=5.0,
        )

        quiz1 = QuizService.create_quiz(
            course_id=created_courses[0].id,
            title="Quiz 1: Python Architecture & SOLID Principles",
            description="Assess your understanding of enterprise Python design patterns and SOLID principles.",
            time_limit_minutes=15,
            passing_percentage=60.0,
        )
        QuizService.add_question_to_quiz(quiz1.id, q1.id)
        QuizService.add_question_to_quiz(quiz1.id, q2.id)

        # -------------------------------------------------------------
        # 4. ASSIGNMENTS
        # -------------------------------------------------------------
        print("[SEED] Creating assignments...")
        assign1 = AssignmentService.create_assignment(
            course_id=created_courses[0].id,
            title="Lab Project 1: Repository Pattern Implementation",
            instructions="Implement a clean Repository Pattern with Unit of Work in Python. Ensure all CRUD methods are covered by automated unit tests.",
            due_date=datetime.now() + timedelta(days=14),
            max_marks=100.0,
        )

        # -------------------------------------------------------------
        # 5. ENROLLMENTS, PROGRESS & ATTENDANCE
        # -------------------------------------------------------------
        print("[SEED] Enrolling students, calculating progress, and generating certificates...")
        for s in students:
            # Enroll in Course 1
            e1 = EnrollmentService.enroll_student(created_courses[0].id, s.id)
            
            # Simulate lesson completions for Alex
            if s.user.username == "student_alex":
                for m in created_courses[0].modules:
                    for l in m.lessons:
                        ProgressService.mark_lesson_completed(e1.id, l.id)

                # Submit Quiz
                attempt = QuizService.start_quiz_attempt(quiz1.id, s.id)
                QuizService.submit_quiz_attempt(
                    attempt.id,
                    {
                        q1.id: "Dependency Inversion Principle (DIP)",
                        q2.id: "False",
                    },
                )

                # Submit Assignment
                sub = AssignmentService.submit_work(
                    assignment_id=assign1.id,
                    student_id=s.id,
                    submission_text="""class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter_by(id=user_id).first()
""",
                )
                AssignmentService.grade_submission(
                    submission_id=sub.id,
                    score=95.0,
                    instructor_feedback="Outstanding architecture and clean SOLID adherence!",
                    letter_grade="A",
                    graded_by=instructors[0].user_id,
                )

                # Record Attendance
                att_sess = AttendanceService.create_session(
                    course_id=created_courses[0].id,
                    title="Introduction & Architecture Lecture",
                    session_date=date.today() - timedelta(days=2),
                )
                AttendanceService.record_attendance(att_sess.id, s.id, status="present")

                # Compute Final Grade & Certificate
                GradingService.calculate_student_grade(created_courses[0].id, s.id)
                CertificateService.generate_certificate(created_courses[0].id, s.id)

            elif s.user.username == "student_sarah":
                # Partial progress
                first_lesson = created_courses[0].modules[0].lessons[0]
                ProgressService.mark_lesson_completed(e1.id, first_lesson.id)

        # -------------------------------------------------------------
        # 6. DISCUSSIONS, CALENDAR & NOTIFICATIONS
        # -------------------------------------------------------------
        print("[SEED] Seeding discussions, calendar events, and notifications...")
        topic = DiscussionService.create_topic(
            course_id=created_courses[0].id,
            user_id=students[0].user_id,
            title="Best practices for Dependency Inversion in Python 3.12?",
            content="When designing service layers, should we prefer abstract base classes (abc.ABC) or typing.Protocol for dependency inversion?",
        )
        DiscussionService.add_reply(
            topic_id=topic.id,
            user_id=instructors[0].user_id,
            content="Both are excellent! typing.Protocol provides structural subtyping (duck typing) without explicit inheritance, while abc.ABC enforces nominal subtyping at runtime.",
            is_instructor_answer=True,
        )

        CalendarService.create_event(
            title="CS-101: Live Design Patterns Workshop",
            start_time=datetime.now() + timedelta(days=3, hours=2),
            end_time=datetime.now() + timedelta(days=3, hours=4),
            event_type="Class",
            course_id=created_courses[0].id,
            description="Interactive walkthrough on Dependency Injection and Repository patterns.",
        )

        for s in students:
            NotificationService.send_notification(
                user_id=s.user_id,
                title="Welcome to the Enterprise LMS Platform!",
                message="Your student profile is active. Browse the course catalog to enroll in accredited courses.",
                category="System",
            )

        print("[SEED] Seed data population completed successfully!")


if __name__ == "__main__":
    reset_requested = "--reset" in sys.argv or "-r" in sys.argv
    run_seed(reset=reset_requested)
