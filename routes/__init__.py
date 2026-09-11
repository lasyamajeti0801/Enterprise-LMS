"""Routes package aggregator."""

from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.common_routes import common_bp
from routes.instructor_routes import instructor_bp
from routes.student_routes import student_bp

__all__ = ["auth_bp", "admin_bp", "instructor_bp", "student_bp", "common_bp"]
