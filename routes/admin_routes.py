"""Admin portal routes: Platform governance, user management, course approvals, audit logs, and settings."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from analytics.services import AnalyticsService
from audit.services import AuditService
from core.database import get_session
from core.security import role_required
from courses.services import CourseService
from instructors.services import InstructorService
from roles.services import RoleService
from settings.services import SettingService
from students.services import StudentService
from users.services import UserService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@role_required("admin")
def enforce_admin():
    """Ensure all admin endpoints require authenticated Administrator role."""
    pass


@admin_bp.route("/dashboard")
def dashboard():
    """Administrator Overview Dashboard."""
    analytics = AnalyticsService.get_admin_analytics()
    recent_logs = AuditService.get_logs(page=1, per_page=8).items
    pending_courses = CourseService.list_all_courses(status="pending_approval", per_page=5).items
    pending_instructors = InstructorService.get_all_instructors(status="pending_approval", per_page=5).items

    return render_template(
        "admin/dashboard.html",
        analytics=analytics,
        recent_logs=recent_logs,
        pending_courses=pending_courses,
        pending_instructors=pending_instructors,
    )


@admin_bp.route("/users")
def users():
    """User Management List with filtering."""
    query_str = request.args.get("q", "")
    role_name = request.args.get("role", "")
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    page_data = UserService.search_users(query_str=query_str, role_name=role_name, status=status, page=page, per_page=15)
    roles = RoleService.get_all_roles()

    return render_template(
        "admin/users.html",
        page_data=page_data,
        roles=roles,
        current_q=query_str,
        current_role=role_name,
        current_status=status,
    )


@admin_bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    """Create a new user account."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        role_name = request.form.get("role_name", "student")

        try:
            user = UserService.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_name=role_name,
            )
            if role_name == "student":
                StudentService.create_or_get_profile(user.id)
            elif role_name == "instructor":
                InstructorService.create_or_get_profile(user.id)

            AuditService.log_action(
                action="USER_CREATED",
                entity_type="User",
                entity_id=user.id,
                user_id=session.get("user_id"),
                new_values={"username": username, "role": role_name},
            )
            flash(f"User '{username}' created successfully.", "success")
            return redirect(url_for("admin.users"))
        except Exception as e:
            flash(str(e), "danger")

    roles = RoleService.get_all_roles()
    return render_template("admin/user_create.html", roles=roles)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
def toggle_user_status(user_id):
    """Toggle user active/suspended state."""
    user = UserService.get_by_id(user_id)
    new_status = "suspended" if user.status == "active" else "active"
    UserService.update_user(user_id, status=new_status)

    AuditService.log_action(
        action="USER_STATUS_CHANGE",
        entity_type="User",
        entity_id=user_id,
        user_id=session.get("user_id"),
        old_values={"status": user.status},
        new_values={"status": new_status},
    )
    flash(f"User status updated to '{new_status}'.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/courses")
def courses():
    """Course catalog administration and approval queue."""
    status = request.args.get("status", "")
    query_str = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)

    page_data = CourseService.list_all_courses(status=status, query_str=query_str, page=page, per_page=15)
    return render_template("admin/courses.html", page_data=page_data, current_status=status, current_q=query_str)


@admin_bp.route("/courses/<int:course_id>/approve", methods=["POST"])
def approve_course(course_id):
    """Approve a submitted course."""
    CourseService.approve_course(course_id)
    AuditService.log_action(
        action="COURSE_APPROVED",
        entity_type="Course",
        entity_id=course_id,
        user_id=session.get("user_id"),
    )
    flash("Course has been approved successfully.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/<int:course_id>/reject", methods=["POST"])
def reject_course(course_id):
    """Reject a submitted course with reasons."""
    reason = request.form.get("reason", "Content does not meet platform curriculum standards.")
    CourseService.reject_course(course_id, reason=reason)
    AuditService.log_action(
        action="COURSE_REJECTED",
        entity_type="Course",
        entity_id=course_id,
        user_id=session.get("user_id"),
        new_values={"reason": reason},
    )
    flash("Course has been rejected.", "warning")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/<int:course_id>/publish", methods=["POST"])
def publish_course(course_id):
    """Publish an approved course."""
    CourseService.publish_course(course_id)
    AuditService.log_action(
        action="COURSE_PUBLISHED",
        entity_type="Course",
        entity_id=course_id,
        user_id=session.get("user_id"),
    )
    flash("Course published to public catalog.", "success")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/instructors")
def instructors():
    """Instructor governance and approval list."""
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    page_data = InstructorService.get_all_instructors(status=status, page=page, per_page=15)
    return render_template("admin/instructors.html", page_data=page_data, current_status=status)


@admin_bp.route("/instructors/<int:instructor_id>/status", methods=["POST"])
def set_instructor_status(instructor_id):
    """Approve or reject instructor application."""
    status = request.form.get("status", "approved")
    InstructorService.set_approval_status(instructor_id, status=status)
    flash(f"Instructor status changed to '{status}'.", "info")
    return redirect(url_for("admin.instructors"))


@admin_bp.route("/audit")
@admin_bp.route("/audit-logs")
def audit_logs():
    """Audit log inspection."""
    action = request.args.get("action", "")
    page = request.args.get("page", 1, type=int)
    page_data = AuditService.get_logs(action=action, page=page, per_page=20)
    return render_template("admin/audit_logs.html", page_data=page_data, current_action=action)


@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Platform system settings editor."""
    if request.method == "POST":
        for key, val in request.form.items():
            if not key.startswith("csrf_"):
                SettingService.set_setting(key, val)
        flash("Platform settings saved successfully.", "success")
        return redirect(url_for("admin.settings"))

    all_settings = SettingService.get_all_settings()
    return render_template("admin/settings.html", settings=all_settings)


@admin_bp.route("/reports")
def reports():
    """Reports overview and CSV export links."""
    return render_template("admin/reports.html")
