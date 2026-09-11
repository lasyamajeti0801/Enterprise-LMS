"""Instructor portal routes: Course authoring, curriculum hierarchy, assignment & quiz grading, attendance, and analytics."""

from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from analytics.services import AnalyticsService
from assignments.services import AssignmentService
from attendance.services import AttendanceService
from core.exceptions import ValidationError
from core.security import role_required
from courses.services import CourseService
from examinations.services import ExaminationService
from grading.services import GradingService
from instructors.services import InstructorService
from lessons.services import LessonService
from modules.services import ModuleService
from question_bank.services import QuestionBankService
from quizzes.services import QuizService
from submissions.models import AssignmentSubmission

instructor_bp = Blueprint("instructor", __name__, url_prefix="/instructor")


@instructor_bp.before_request
@role_required("instructor")
def enforce_instructor():
    """Ensure all instructor endpoints require authenticated Instructor role."""
    pass


def _get_current_instructor_id():
    profile = InstructorService.get_by_user_id(session["user_id"])
    if not profile:
        profile = InstructorService.create_or_get_profile(session["user_id"])
    return profile.id


@instructor_bp.route("/dashboard")
def dashboard():
    """Instructor overview dashboard."""
    inst_id = _get_current_instructor_id()
    analytics = AnalyticsService.get_instructor_analytics(inst_id)
    my_courses = CourseService.list_instructor_courses(inst_id, per_page=6).items

    return render_template("instructor/dashboard.html", analytics=analytics, courses=my_courses)


@instructor_bp.route("/courses")
def courses():
    """Instructor's course list."""
    inst_id = _get_current_instructor_id()
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    page_data = CourseService.list_instructor_courses(inst_id, status=status, page=page, per_page=12)
    return render_template("instructor/courses.html", page_data=page_data, current_status=status)


@instructor_bp.route("/courses/create", methods=["GET", "POST"])
def create_course():
    """Create a new course wizard."""
    inst_id = _get_current_instructor_id()
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        title = request.form.get("title", "").strip()
        short_desc = request.form.get("short_description", "").strip()
        full_desc = request.form.get("full_description", "").strip()
        category = request.form.get("category", "Computer Science")
        difficulty = request.form.get("difficulty", "Beginner")
        duration = request.form.get("duration_hours", 20, type=int)
        capacity = request.form.get("capacity", 100, type=int)
        passing_grade = request.form.get("passing_grade", 60.0, type=float)
        prerequisites = request.form.get("prerequisites", "")
        learning_objectives = request.form.get("learning_objectives", "")

        try:
            course = CourseService.create_course(
                code=code,
                title=title,
                short_description=short_desc,
                full_description=full_desc,
                instructor_id=inst_id,
                category=category,
                difficulty=difficulty,
                duration_hours=duration,
                capacity=capacity,
                passing_grade=passing_grade,
                prerequisites=prerequisites,
                learning_objectives=learning_objectives,
                status="draft",
            )
            flash(f"Course '{course.title}' created as Draft. Now add modules and lessons.", "success")
            return redirect(url_for("instructor.curriculum", course_id=course.id))
        except ValidationError as e:
            flash(str(e.message), "danger")
        except Exception as e:
            flash(f"Failed to create course: {str(e)}", "danger")

    return render_template("instructor/course_create.html")


@instructor_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id):
    """Edit course details."""
    course = CourseService.get_by_id(course_id)
    if request.method == "POST":
        CourseService.update_course(
            course_id,
            title=request.form.get("title"),
            short_description=request.form.get("short_description"),
            full_description=request.form.get("full_description"),
            category=request.form.get("category"),
            difficulty=request.form.get("difficulty"),
            duration_hours=request.form.get("duration_hours", type=int),
            capacity=request.form.get("capacity", type=int),
            passing_grade=request.form.get("passing_grade", type=float),
            prerequisites=request.form.get("prerequisites"),
            learning_objectives=request.form.get("learning_objectives"),
        )
        flash("Course details updated successfully.", "success")
        return redirect(url_for("instructor.courses"))

    return render_template("instructor/course_edit.html", course=course)


@instructor_bp.route("/courses/<int:course_id>/submit", methods=["POST"])
def submit_course(course_id):
    """Submit course for Administrator review."""
    CourseService.submit_for_approval(course_id)
    flash("Course submitted for administrator approval.", "info")
    return redirect(url_for("instructor.courses"))


@instructor_bp.route("/courses/<int:course_id>/curriculum")
def curriculum(course_id):
    """Curriculum hierarchy editor."""
    course = CourseService.get_by_id(course_id)
    return render_template("instructor/curriculum_edit.html", course=course)


@instructor_bp.route("/courses/<int:course_id>/modules/create", methods=["POST"])
def create_module(course_id):
    """Add a module to course."""
    title = request.form.get("title", "").strip()
    desc = request.form.get("description", "").strip()
    if title:
        ModuleService.create_module(course_id=course_id, title=title, description=desc)
        flash(f"Module '{title}' created.", "success")
    return redirect(url_for("instructor.curriculum", course_id=course_id))


@instructor_bp.route("/modules/<int:module_id>/lessons/create", methods=["POST"])
def create_lesson(module_id):
    """Add a lesson to module."""
    module = ModuleService.get_by_id(module_id)
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    summary = request.form.get("summary", "").strip()
    content_type = request.form.get("content_type", "text")
    duration = request.form.get("duration_minutes", 15, type=int)

    if title and content:
        LessonService.create_lesson(
            module_id=module_id,
            title=title,
            content=content,
            summary=summary,
            content_type=content_type,
            duration_minutes=duration,
        )
        flash(f"Lesson '{title}' created.", "success")
    return redirect(url_for("instructor.curriculum", course_id=module.course_id))


@instructor_bp.route("/assignments")
@instructor_bp.route("/assignments/<int:course_id>")
@instructor_bp.route("/courses/<int:course_id>/assignments")
def assignments(course_id=None):
    """Manage course assignments."""
    if course_id is None:
        inst_id = _get_current_instructor_id()
        courses = CourseService.list_instructor_courses(inst_id, per_page=1).items
        if courses:
            return redirect(url_for("instructor.assignments", course_id=courses[0].id))
        flash("You have no courses yet to manage assignments for.", "warning")
        return redirect(url_for("instructor.courses"))
    course = CourseService.get_by_id(course_id)
    return render_template("instructor/assignments.html", course=course)


@instructor_bp.route("/courses/<int:course_id>/assignments/create", methods=["GET", "POST"])
def create_assignment(course_id):
    """Create a new assignment."""
    course = CourseService.get_by_id(course_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        instructions = request.form.get("instructions", "").strip()
        due_str = request.form.get("due_date", "")
        max_marks = request.form.get("max_marks", 100.0, type=float)

        try:
            due_date = datetime.fromisoformat(due_str) if due_str else datetime.now()
            AssignmentService.create_assignment(
                course_id=course_id,
                title=title,
                instructions=instructions,
                due_date=due_date,
                max_marks=max_marks,
            )
            flash(f"Assignment '{title}' created.", "success")
            return redirect(url_for("instructor.assignments", course_id=course_id))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("instructor/assignment_create.html", course=course)


@instructor_bp.route("/assignments/<int:assignment_id>/submissions")
def assignment_submissions(assignment_id):
    """View and grade submissions for an assignment."""
    assignment = AssignmentService.get_by_id(assignment_id)
    return render_template("instructor/assignment_submissions.html", assignment=assignment)


@instructor_bp.route("/submissions/<int:submission_id>/grade", methods=["POST"])
def grade_submission(submission_id):
    """Submit grade and feedback for student submission."""
    score = request.form.get("score", type=float)
    feedback = request.form.get("feedback", "")
    letter_grade = request.form.get("letter_grade")

    AssignmentService.grade_submission(
        submission_id=submission_id,
        score=score,
        instructor_feedback=feedback,
        letter_grade=letter_grade,
        graded_by=session.get("user_id"),
    )
    flash("Submission graded successfully.", "success")
    submission = AssignmentSubmission.query.get(submission_id)
    return redirect(url_for("instructor.assignment_submissions", assignment_id=submission.assignment_id))


@instructor_bp.route("/quizzes")
@instructor_bp.route("/quizzes/<int:course_id>")
@instructor_bp.route("/courses/<int:course_id>/quizzes")
def quizzes(course_id=None):
    """Manage quizzes."""
    if course_id is None:
        inst_id = _get_current_instructor_id()
        courses = CourseService.list_instructor_courses(inst_id, per_page=1).items
        if courses:
            return redirect(url_for("instructor.quizzes", course_id=courses[0].id))
        flash("You have no courses yet to manage quizzes for.", "warning")
        return redirect(url_for("instructor.courses"))
    course = CourseService.get_by_id(course_id)
    return render_template("instructor/quizzes.html", course=course)


@instructor_bp.route("/courses/<int:course_id>/quizzes/create", methods=["GET", "POST"])
def create_quiz(course_id):
    """Create a new quiz and link questions."""
    course = CourseService.get_by_id(course_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        time_limit = request.form.get("time_limit_minutes", 20, type=int)
        passing_pct = request.form.get("passing_percentage", 60.0, type=float)

        quiz = QuizService.create_quiz(
            course_id=course_id,
            title=title,
            description=desc,
            time_limit_minutes=time_limit,
            passing_percentage=passing_pct,
        )

        # Quick add sample questions from bank or inline
        q1_prompt = request.form.get("q1_prompt")
        if q1_prompt:
            q1 = QuestionBankService.create_question(
                prompt=q1_prompt,
                options=[request.form.get(f"q1_opt_{i}") for i in range(4) if request.form.get(f"q1_opt_{i}")],
                correct_answers=[request.form.get("q1_correct")],
                category_name=course.category,
            )
            QuizService.add_question_to_quiz(quiz.id, q1.id)

        flash(f"Quiz '{title}' created successfully.", "success")
        return redirect(url_for("instructor.quizzes", course_id=course_id))

    return render_template("instructor/quiz_create.html", course=course)


@instructor_bp.route("/attendance")
@instructor_bp.route("/attendance/<int:course_id>", methods=["GET", "POST"])
@instructor_bp.route("/courses/<int:course_id>/attendance", methods=["GET", "POST"])
def attendance(course_id=None):
    """Attendance session manager."""
    if course_id is None:
        inst_id = _get_current_instructor_id()
        courses = CourseService.list_instructor_courses(inst_id, per_page=1).items
        if courses:
            return redirect(url_for("instructor.attendance", course_id=courses[0].id))
        flash("You have no courses yet to record attendance for.", "warning")
        return redirect(url_for("instructor.courses"))

    course = CourseService.get_by_id(course_id)
    if request.method == "POST":
        title = request.form.get("title", "Lecture Session")
        session_date = datetime.strptime(request.form.get("session_date"), "%Y-%m-%d").date()
        att_session = AttendanceService.create_session(course_id=course_id, title=title, session_date=session_date)

        # Record attendance for enrolled students
        for enrollment in course.enrollments:
            status = request.form.get(f"student_{enrollment.student_id}", "present")
            AttendanceService.record_attendance(
                session_id=att_session.id,
                student_id=enrollment.student_id,
                status=status,
                recorded_by=session.get("user_id"),
            )
        flash("Attendance session recorded successfully.", "success")
        return redirect(url_for("instructor.attendance", course_id=course_id))

    sessions = AttendanceService.get_course_sessions(course_id).items
    return render_template("instructor/attendance.html", course=course, sessions=sessions)


@instructor_bp.route("/gradebook")
@instructor_bp.route("/gradebook/<int:course_id>")
@instructor_bp.route("/courses/<int:course_id>/gradebook")
def gradebook(course_id=None):
    """Course gradebook and weighted evaluation table."""
    if course_id is None:
        inst_id = _get_current_instructor_id()
        courses = CourseService.list_instructor_courses(inst_id, per_page=1).items
        if courses:
            return redirect(url_for("instructor.gradebook", course_id=courses[0].id))
        flash("You have no courses yet to display a gradebook for.", "warning")
        return redirect(url_for("instructor.courses"))

    course = CourseService.get_by_id(course_id)
    scheme = GradingService.get_or_create_scheme(course_id)

    grades = []
    for e in course.enrollments:
        g_rec = GradingService.calculate_student_grade(course_id, e.student_id)
        grades.append({"enrollment": e, "grade": g_rec})

    return render_template("instructor/gradebook.html", course=course, scheme=scheme, grades=grades)
