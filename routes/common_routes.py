"""Common application routes: Global search, discussions, calendar, notifications, public verification, and export endpoints."""

from flask import Blueprint, Response, flash, redirect, render_template, request, session, url_for
from calendar_events.services import CalendarService
from certificates.services import CertificateService
from core.security import login_required
from courses.services import CourseService
from discussions.services import DiscussionService
from notifications.services import NotificationService
from reports.services import ReportService
from search.services import SearchService

common_bp = Blueprint("common", __name__, url_prefix="")


@common_bp.route("/search")
@login_required
def search():
    """Global multi-domain search view."""
    query_str = request.args.get("q", "")
    results = SearchService.global_search(query_str=query_str, limit=20)
    return render_template("common/search_results.html", query=query_str, results=results)


@common_bp.route("/discussions/<int:course_id>")
@login_required
def discussions(course_id):
    """Course discussion forum."""
    course = CourseService.get_by_id(course_id)
    page = request.args.get("page", 1, type=int)
    page_data = DiscussionService.get_course_topics(course_id, page=page, per_page=15)
    return render_template("common/discussions.html", course=course, page_data=page_data)


@common_bp.route("/discussions/<int:course_id>/topics/create", methods=["POST"])
@login_required
def create_topic(course_id):
    """Create a new discussion topic."""
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if title and content:
        topic = DiscussionService.create_topic(course_id=course_id, user_id=session["user_id"], title=title, content=content)
        flash("Discussion topic created.", "success")
        return redirect(url_for("common.topic_detail", topic_id=topic.id))
    flash("Title and content are required.", "warning")
    return redirect(url_for("common.discussions", course_id=course_id))


@common_bp.route("/discussions/topic/<int:topic_id>", methods=["GET", "POST"])
@login_required
def topic_detail(topic_id):
    """View discussion topic and post replies."""
    topic = DiscussionService.get_by_id(topic_id)
    if request.method == "POST":
        reply_content = request.form.get("content", "").strip()
        is_instructor = session.get("user_role") == "instructor"
        if reply_content:
            DiscussionService.add_reply(
                topic_id=topic_id,
                user_id=session["user_id"],
                content=reply_content,
                is_instructor_answer=is_instructor,
            )
            flash("Reply posted.", "success")
            return redirect(url_for("common.topic_detail", topic_id=topic_id))

    return render_template("common/topic_detail.html", topic=topic)


@common_bp.route("/calendar")
@login_required
def calendar_view():
    """Academic calendar and schedule view."""
    events = CalendarService.get_upcoming_events(user_id=session.get("user_id"), days_ahead=60)
    return render_template("common/calendar.html", events=events)


@common_bp.route("/notifications")
@login_required
def notifications():
    """Notification inbox."""
    page = request.args.get("page", 1, type=int)
    page_data = NotificationService.get_user_notifications(user_id=session["user_id"], page=page, per_page=20)
    return render_template("common/notifications.html", page_data=page_data)


@common_bp.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    """Mark all user notifications as read."""
    NotificationService.mark_all_as_read(user_id=session["user_id"])
    flash("All notifications marked as read.", "info")
    return redirect(url_for("common.notifications"))


@common_bp.route("/verify", methods=["GET", "POST"])
@common_bp.route("/verify-certificate", methods=["GET", "POST"])
@common_bp.route("/certificates/verify", methods=["GET", "POST"])
@common_bp.route("/verify-certificate/<verification_code>", methods=["GET", "POST"])
@common_bp.route("/certificates/verify/<verification_code>", methods=["GET", "POST"])
def verify_certificate(verification_code=None):
    """Public certificate verification portal."""
    code = verification_code or request.args.get("code") or request.form.get("code")
    cert_info = None
    if code:
        cert_info = CertificateService.verify_certificate(code.strip())
    return render_template("common/verify_certificate.html", cert_info=cert_info, code=code)


@common_bp.route("/export/<report_type>")
@login_required
def export_report(report_type):
    """Export dataset report as downloadable CSV or JSON."""
    if report_type == "students":
        csv_data = ReportService.export_students_csv()
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=students_report.csv"})
    elif report_type == "courses":
        csv_data = ReportService.export_courses_csv()
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=courses_report.csv"})
    elif report_type == "grades":
        csv_data = ReportService.export_grades_csv()
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=grades_report.csv"})
    elif report_type == "audit":
        json_data = ReportService.export_audit_logs_json()
        return Response(json_data, mimetype="application/json", headers={"Content-Disposition": "attachment;filename=audit_logs.json"})

    flash("Unknown export format requested.", "danger")
    return redirect(request.referrer or url_for("auth.landing"))
