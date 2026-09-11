"""End-to-End Workflow verification tests across Admin, Instructor, and Student portals."""

import pytest
from assignments.services import AssignmentService
from certificates.services import CertificateService
from courses.services import CourseService
from enrollment.services import EnrollmentService
from grading.services import GradingService
from instructors.services import InstructorService
from lessons.services import LessonService
from modules.services import ModuleService
from progress.services import ProgressService
from question_bank.services import QuestionBankService
from quizzes.services import QuizService
from students.services import StudentService
from users.services import UserService


def test_admin_end_to_end_workflow(db_session, client, sample_admin):
    """Verify Admin workflow: Login -> Dashboard -> Create Faculty -> Approve Course -> Reports."""
    # 1. Admin Login
    res = client.post("/auth/login/admin", data={"identifier": "test_admin", "password": "adminpassword123"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Administrator Dashboard" in res.data

    # 2. Create Instructor
    inst_user = UserService.create_user(
        username="e2e_instructor",
        email="e2e_inst@lms.local",
        password="password123",
        first_name="Alan",
        last_name="Turing",
        role_name="instructor",
    )
    inst_prof = InstructorService.create_or_get_profile(inst_user.id)
    assert inst_prof.id is not None

    # 3. Create Draft Course & Approve
    course = CourseService.create_course(
        code="E2E-101",
        title="End to End Systems",
        short_description="Short",
        full_description="Full",
        instructor_id=inst_prof.id,
        status="pending_approval",
    )
    approve_res = client.post(f"/admin/courses/{course.id}/approve", follow_redirects=True)
    assert approve_res.status_code == 200
    assert course.status == "approved"

    # 4. View Reports
    reports_res = client.get("/admin/reports")
    assert reports_res.status_code == 200
    assert b"Institutional Reports" in reports_res.data


def test_instructor_end_to_end_workflow(db_session, client, sample_instructor, sample_student):
    """Verify Instructor workflow: Login -> Create Course -> Curriculum -> Assignment -> Grade."""
    inst_user, inst_prof = sample_instructor
    _, std_prof = sample_student

    # 1. Instructor Login
    res = client.post("/auth/login/instructor", data={"identifier": "test_instructor", "password": "instpassword123"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Instructor Dashboard" in res.data

    # 2. Create Course & Curriculum
    course = CourseService.create_course(
        code="CS-301",
        title="Compiler Design",
        short_description="Lexing, parsing, code gen",
        full_description="Building modern compilers",
        instructor_id=inst_prof.id,
        status="published",
    )
    mod = ModuleService.create_module(course.id, "Module 1: Lexical Analysis")
    lesson = LessonService.create_lesson(mod.id, "Lexer Implementation", "Lexer token stream notes.")
    assert lesson.id is not None

    # 3. Create Assignment & Quiz
    assign = AssignmentService.create_assignment(course.id, "Lexer Project", "Build a lexer in Python", due_date=None, max_marks=100.0)
    q_item = QuestionBankService.create_question("Is a DFA deterministic?", "mcq_single", options=["Yes", "No"], correct_answers=["Yes"], marks=10.0)
    quiz = QuizService.create_quiz(course.id, "Lexer Quiz")
    QuizService.add_question_to_quiz(quiz.id, q_item.id)

    # 4. Student Submits & Instructor Grades
    sub = AssignmentService.submit_work(assign.id, std_prof.id, "class Lexer: pass")
    graded = AssignmentService.grade_submission(sub.id, score=98.0, instructor_feedback="Excellent!", letter_grade="A", graded_by=inst_user.id)
    assert graded.status == "graded"
    assert graded.score == 98.0


def test_student_end_to_end_workflow(db_session, client, sample_instructor, sample_student):
    """Verify Student workflow: Login -> Browse -> Enroll -> Learn -> Quiz -> Certificate."""
    _, inst_prof = sample_instructor
    std_user, std_prof = sample_student

    # Create published course
    course = CourseService.create_course(
        code="CS-100",
        title="Intro to Computing",
        short_description="Basics of CS",
        full_description="Introductory curriculum",
        instructor_id=inst_prof.id,
        status="published",
    )
    mod = ModuleService.create_module(course.id, "Module 1")
    lesson = LessonService.create_lesson(mod.id, "Binary Numbers", "Binary representation notes.")
    q = QuestionBankService.create_question("What is 1 + 1 in binary?", "mcq_single", options=["10", "2", "11"], correct_answers=["10"], marks=10.0)
    quiz = QuizService.create_quiz(course.id, "Binary Quiz")
    QuizService.add_question_to_quiz(quiz.id, q.id)

    # 1. Student Login
    res = client.post("/auth/login/student", data={"identifier": "test_student", "password": "stdpassword123"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Student Dashboard" in res.data or b"Welcome" in res.data

    # 2. Enroll
    enroll_res = client.post(f"/student/enroll/{course.id}", follow_redirects=True)
    assert enroll_res.status_code == 200

    # 3. Complete Lesson
    enrollment = EnrollmentService.get_enrollment(course.id, std_prof.id)
    ProgressService.mark_lesson_completed(enrollment.id, lesson.id)
    assert enrollment.progress_percentage == 100.0

    # 4. Take Quiz
    attempt = QuizService.start_quiz_attempt(quiz.id, std_prof.id)
    QuizService.submit_quiz_attempt(attempt.id, {q.id: "10"})
    assert attempt.is_passed is True

    # 5. Calculate Final Grade and Claim Certificate
    GradingService.calculate_student_grade(course.id, std_prof.id)
    cert = CertificateService.generate_certificate(course.id, std_prof.id)
    assert cert.id is not None
    assert cert.verification_code.startswith("LMS-")
