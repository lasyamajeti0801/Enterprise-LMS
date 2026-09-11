"""Student portal routes: Course catalog, learning player, quiz/exam runner, assignments, grades, and certificates."""

from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for
from analytics.services import AnalyticsService
from assignments.services import AssignmentService
from attendance.services import AttendanceService
from certificates.services import CertificateService
from core.exceptions import AssessmentError, CertificateIneligibleError, EnrollmentError
from core.security import role_required
from courses.services import CourseService
from enrollment.services import EnrollmentService
from gamification.services import GamificationService
from grading.services import GradingService
from lessons.services import LessonService
from progress.services import ProgressService
from quizzes.services import QuizService
from students.services import StudentService

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.before_request
@role_required("student")
def enforce_student():
    """Ensure all student endpoints require authenticated Student role."""
    pass


def _get_current_student_id():
    profile = StudentService.get_by_user_id(session["user_id"])
    if not profile:
        profile = StudentService.create_or_get_profile(session["user_id"])
    return profile.id


@student_bp.route("/dashboard")
def dashboard():
    """Student Home Dashboard."""
    student_id = _get_current_student_id()
    analytics = AnalyticsService.get_student_analytics(student_id)
    enrollments = EnrollmentService.get_student_enrollments(student_id, per_page=6).items
    badges = GamificationService.get_user_badges(session["user_id"])
    leaderboard = GamificationService.get_leaderboard(limit=5)

    return render_template(
        "student/dashboard.html",
        analytics=analytics,
        enrollments=enrollments,
        badges=badges,
        leaderboard=leaderboard,
    )


@student_bp.route("/catalog")
def catalog():
    """Browse public course catalog."""
    category = request.args.get("category", "")
    difficulty = request.args.get("difficulty", "")
    query_str = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)

    page_data = CourseService.list_published_courses(
        category=category,
        difficulty=difficulty,
        query_str=query_str,
        page=page,
        per_page=12,
    )
    return render_template(
        "student/catalog.html",
        page_data=page_data,
        current_cat=category,
        current_diff=difficulty,
        current_q=query_str,
    )


@student_bp.route("/courses/<slug>")
def course_detail(slug):
    """View course syllabus and enrollment CTA."""
    course = CourseService.get_by_slug(slug)
    student_id = _get_current_student_id()
    enrollment = EnrollmentService.get_enrollment(course.id, student_id)
    return render_template("student/course_detail.html", course=course, enrollment=enrollment)


@student_bp.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    """Enroll in a course."""
    student_id = _get_current_student_id()
    try:
        enrollment = EnrollmentService.enroll_student(course_id=course_id, student_id=student_id)
        flash("Successfully enrolled in course! You can now begin learning.", "success")
        return redirect(url_for("student.learn_course", course_id=course_id))
    except EnrollmentError as e:
        flash(str(e.message), "danger")
        return redirect(request.referrer or url_for("student.catalog"))


@student_bp.route("/learn/<int:course_id>")
@student_bp.route("/learn/<int:course_id>/<int:lesson_id>")
def learn_course(course_id, lesson_id=None):
    """Interactive Learning Player with curriculum tree and lesson content."""
    student_id = _get_current_student_id()
    course = CourseService.get_by_id(course_id)
    enrollment = EnrollmentService.get_enrollment(course_id, student_id)

    if not enrollment or enrollment.status not in ("active", "completed"):
        flash("Please enroll in this course first to access the learning player.", "warning")
        return redirect(url_for("student.course_detail", slug=course.slug))

    # Pick target lesson
    current_lesson = None
    if lesson_id:
        current_lesson = LessonService.get_by_id(lesson_id)
    else:
        # Default to first lesson of first module
        if course.modules and course.modules[0].lessons:
            current_lesson = course.modules[0].lessons[0]

    completed_ids = ProgressService.get_completed_lesson_ids(enrollment.id)

    return render_template(
        "student/learn_player.html",
        course=course,
        enrollment=enrollment,
        current_lesson=current_lesson,
        completed_ids=completed_ids,
    )


@student_bp.route("/progress/complete-lesson", methods=["POST"])
def complete_lesson():
    """Mark a lesson as completed."""
    enrollment_id = request.form.get("enrollment_id", type=int)
    lesson_id = request.form.get("lesson_id", type=int)

    result = ProgressService.mark_lesson_completed(enrollment_id=enrollment_id, lesson_id=lesson_id)
    flash("Lesson completed! Progress updated.", "success")
    enrollment = EnrollmentService.get_student_enrollments(_get_current_student_id()).items
    return redirect(request.referrer or url_for("student.dashboard"))


@student_bp.route("/assignments")
def assignments():
    """List pending and completed student assignments."""
    student_id = _get_current_student_id()
    enrollments = EnrollmentService.get_student_enrollments(student_id).items
    course_ids = [e.course_id for e in enrollments]

    from assignments.models import Assignment
    course_assignments = (
        Assignment.query.filter(Assignment.course_id.in_(course_ids), Assignment.is_published == True)
        .order_by(Assignment.due_date.asc())
        .all()
    ) if course_ids else []

    return render_template("student/assignments.html", assignments=course_assignments, student_id=student_id)


@student_bp.route("/assignments/<int:assignment_id>/submit", methods=["GET", "POST"])
def submit_assignment(assignment_id):
    """Submit assignment work."""
    assignment = AssignmentService.get_by_id(assignment_id)
    student_id = _get_current_student_id()

    if request.method == "POST":
        submission_text = request.form.get("submission_text", "")
        try:
            AssignmentService.submit_work(
                assignment_id=assignment_id,
                student_id=student_id,
                submission_text=submission_text,
            )
            flash("Assignment submitted successfully!", "success")
            return redirect(url_for("student.assignments"))
        except AssessmentError as e:
            flash(str(e.message), "danger")

    submission = AssignmentService.get_student_submission(assignment_id, student_id)
    return render_template("student/assignment_submit.html", assignment=assignment, submission=submission)


@student_bp.route("/quizzes/<int:quiz_id>/take", methods=["GET", "POST"])
def take_quiz(quiz_id):
    """Interactive quiz runner with timer and question options."""
    quiz = QuizService.get_by_id(quiz_id)
    student_id = _get_current_student_id()

    if request.method == "POST":
        # Form submission: collect question answers
        raw_answers = {}
        for qq in quiz.questions:
            ans = request.form.get(f"q_{qq.question_id}")
            if ans:
                raw_answers[qq.question_id] = ans

        attempt_id = request.form.get("attempt_id", type=int)
        if not attempt_id:
            attempt = QuizService.start_quiz_attempt(quiz_id, student_id)
            attempt_id = attempt.id

        attempt = QuizService.submit_quiz_attempt(attempt_id, raw_answers)
        return redirect(url_for("student.quiz_result", attempt_id=attempt.id))

    attempt = QuizService.start_quiz_attempt(quiz_id, student_id)
    return render_template("student/quiz_take.html", quiz=quiz, attempt=attempt)


@student_bp.route("/quizzes/results/<int:attempt_id>")
def quiz_result(attempt_id):
    """Display evaluated quiz result with score and answer review."""
    from quizzes.models import QuizAttempt
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    return render_template("student/quiz_result.html", attempt=attempt)


@student_bp.route("/grades")
def grades():
    """Student Grade Report and GPA overview."""
    student_id = _get_current_student_id()
    enrollments = EnrollmentService.get_student_enrollments(student_id).items

    grade_records = []
    for e in enrollments:
        rec = GradingService.calculate_student_grade(e.course_id, student_id)
        grade_records.append({"course": e.course, "grade": rec})

    student_profile = StudentService.get_by_user_id(session["user_id"])
    return render_template("student/grades.html", grade_records=grade_records, profile=student_profile)


@student_bp.route("/certificates")
def certificates():
    """Student Credentials and Certificate download center."""
    student_id = _get_current_student_id()
    enrollments = EnrollmentService.get_student_enrollments(student_id).items

    cert_status = []
    for e in enrollments:
        is_eligible, reason = CertificateService.check_eligibility(e.course_id, student_id)
        existing_cert = next((c for c in e.course.certificates if c.student_id == student_id), None)
        cert_status.append({
            "course": e.course,
            "is_eligible": is_eligible,
            "reason": reason,
            "certificate": existing_cert,
        })

    return render_template("student/certificates.html", cert_status=cert_status)


@student_bp.route("/certificates/<int:course_id>/generate", methods=["POST"])
def generate_certificate(course_id):
    """Generate official PDF certificate."""
    student_id = _get_current_student_id()
    try:
        cert = CertificateService.generate_certificate(course_id=course_id, student_id=student_id)
        flash(f"Certificate {cert.certificate_number} generated successfully!", "success")
    except CertificateIneligibleError as e:
        flash(str(e.message), "warning")
    except Exception as e:
        flash(f"Failed to generate certificate: {str(e)}", "danger")

    return redirect(url_for("student.certificates"))


@student_bp.route("/certificates/<int:course_id>/download")
def download_certificate(course_id):
    """Download generated PDF certificate."""
    student_id = _get_current_student_id()
    cert = next((c for c in CourseService.get_by_id(course_id).certificates if c.student_id == student_id), None)
    if not cert or not cert.pdf_file_path:
        flash("Certificate file not found.", "danger")
        return redirect(url_for("student.certificates"))

    return send_file(cert.pdf_file_path, as_attachment=True, download_name=f"Certificate_{cert.certificate_number}.pdf")


@student_bp.route("/gamification")
def gamification():
    """Gamification Hub with XP, level progression, badges, and leaderboards."""
    user_points = GamificationService.get_or_create_user_points(session["user_id"])
    badges = GamificationService.get_user_badges(session["user_id"])
    leaderboard = GamificationService.get_leaderboard(limit=15)
    return render_template("student/gamification.html", points=user_points, badges=badges, leaderboard=leaderboard)
