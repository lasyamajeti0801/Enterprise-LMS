"""Enterprise Learning Management System - Flask Application Factory."""

import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session
from config.logging_config import setup_logging
from config.settings import BaseConfig, get_config
from core.database import close_session, init_db
from core.exceptions import LMSException
from core.middleware import register_middleware
from notifications.services import NotificationService
from routes import admin_bp, auth_bp, common_bp, instructor_bp, student_bp

# Import all models to ensure declarative base metadata is registered
from roles.models import Permission, Role
from users.models import User
from students.models import StudentProfile
from instructors.models import InstructorProfile
from authentication.models import LoginHistory, PasswordResetToken
from courses.models import Course
from modules.models import CourseModule
from lessons.models import Lesson
from materials.models import LessonMaterial
from enrollment.models import CourseEnrollment
from progress.models import LessonProgress
from attendance.models import AttendanceRecord, AttendanceSession
from question_bank.models import QuestionBankItem, QuestionCategory
from quizzes.models import Quiz, QuizAnswer, QuizAttempt, QuizQuestion
from examinations.models import Exam, ExamAnswer, ExamAttempt
from assignments.models import Assignment
from submissions.models import AssignmentSubmission
from grading.models import FinalGradeRecord, GradingScheme
from certificates.models import Certificate
from gamification.models import Badge, UserBadge, UserPoints
from skills.models import CourseSkill, Skill, StudentSkill
from discussions.models import DiscussionReply, DiscussionTopic
from notifications.models import Notification
from calendar_events.models import CalendarEvent
from audit.models import AuditLog
from settings.models import SystemSetting


def create_app(config_class=None, config_name="development"):
    """Application factory for Enterprise LMS."""
    app = Flask(__name__)

    # Load configuration
    if isinstance(config_class, str):
        config_class = get_config(config_class)
    elif config_class is None:
        config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Ensure runtime directories exist
    config_class.ensure_directories()

    # Logging setup
    setup_logging(app)

    # Initialize database
    init_db(app.config["SQLALCHEMY_DATABASE_URI"])

    # Register middleware
    register_middleware(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(common_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_context():
        unread_count = 0
        user_id = session.get("user_id")
        if user_id:
            try:
                unread_count = NotificationService.get_unread_count(user_id)
            except Exception:
                unread_count = 0

        return {
            "app_name": app.config.get("APP_NAME", "Enterprise LMS"),
            "app_version": app.config.get("APP_VERSION", "2.5.0"),
            "current_year": datetime.now().year,
            "session_user_id": user_id,
            "session_user_name": session.get("user_name"),
            "session_user_role": session.get("user_role"),
            "session_user_email": session.get("user_email"),
            "unread_notifications_count": unread_count,
        }

    # Disable client-side caching for instant UI reload
    @app.after_request
    def set_cache_control_headers(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found", "status": 404}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def handle_forbidden(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Forbidden", "status": 403}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def handle_server_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal Server Error", "status": 500}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(LMSException)
    def handle_lms_domain_exception(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": e.message, "status": e.code, "payload": e.payload}), e.code
        return render_template("errors/domain_error.html", error=e), e.code

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
