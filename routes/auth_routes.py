"""Authentication routes and portal landing views."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from authentication.services import AuthenticationService
from core.exceptions import AuthenticationError, PermissionDeniedError, ValidationError
from core.security import login_required
from users.services import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/")
def landing():
    """Master landing page presenting the THREE dedicated login portals (Admin, Instructor, Student)."""
    if session.get("user_id"):
        role = session.get("user_role", "").lower()
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif role == "instructor":
            return redirect(url_for("instructor.dashboard"))
        elif role == "student":
            return redirect(url_for("student.dashboard"))
    return render_template("landing.html")


@auth_bp.route("/login")
@auth_bp.route("/auth/login")
def login_router():
    """Generic login route that redirects to requested portal or landing page."""
    portal = request.args.get("portal", "").lower().strip()
    if portal in ("admin", "administrator"):
        return redirect(url_for("auth.admin_login"))
    elif portal in ("instructor", "faculty", "prof", "teacher"):
        return redirect(url_for("auth.instructor_login"))
    elif portal in ("student", "learner"):
        return redirect(url_for("auth.student_login"))
    return redirect(url_for("auth.landing"))


@auth_bp.route("/admin-login", methods=["GET", "POST"])
@auth_bp.route("/auth/login/admin", methods=["GET", "POST"])
def admin_login():
    """Admin portal login route."""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        ip_addr = request.remote_addr or "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "Browser")

        try:
            user = AuthenticationService.authenticate_user(
                identifier=identifier,
                password=password,
                expected_role="admin",
                ip_address=ip_addr,
                user_agent=user_agent,
            )
            flash(f"Welcome back, Administrator {user.first_name}!", "success")
            return redirect(url_for("admin.dashboard"))
        except (AuthenticationError, PermissionDeniedError) as e:
            flash(str(e.message), "danger")

    return render_template("auth/admin_login.html")


@auth_bp.route("/instructor-login", methods=["GET", "POST"])
@auth_bp.route("/auth/login/instructor", methods=["GET", "POST"])
def instructor_login():
    """Instructor portal login route."""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        ip_addr = request.remote_addr or "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "Browser")

        try:
            user = AuthenticationService.authenticate_user(
                identifier=identifier,
                password=password,
                expected_role="instructor",
                ip_address=ip_addr,
                user_agent=user_agent,
            )
            flash(f"Welcome back, Instructor {user.first_name}!", "success")
            return redirect(url_for("instructor.dashboard"))
        except (AuthenticationError, PermissionDeniedError) as e:
            flash(str(e.message), "danger")

    return render_template("auth/instructor_login.html")


@auth_bp.route("/student-login", methods=["GET", "POST"])
@auth_bp.route("/auth/login/student", methods=["GET", "POST"])
def student_login():
    """Student portal login route."""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        ip_addr = request.remote_addr or "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "Browser")

        try:
            user = AuthenticationService.authenticate_user(
                identifier=identifier,
                password=password,
                expected_role="student",
                ip_address=ip_addr,
                user_agent=user_agent,
            )
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(url_for("student.dashboard"))
        except (AuthenticationError, PermissionDeniedError) as e:
            flash(str(e.message), "danger")

    return render_template("auth/student_login.html")


@auth_bp.route("/auth/register", methods=["GET", "POST"])
def register():
    """Public student registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        major = request.form.get("major", "Computer Science").strip()

        try:
            user = UserService.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_name="student",
            )
            from students.services import StudentService
            StudentService.create_or_get_profile(user.id, major=major)

            flash("Account registered successfully! You can now log in to the Student Portal.", "success")
            return redirect(url_for("auth.student_login"))
        except ValidationError as e:
            flash(str(e.message), "danger")
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/auth/logout")
def logout():
    """Terminate user session and redirect to landing page."""
    AuthenticationService.logout()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.landing"))
