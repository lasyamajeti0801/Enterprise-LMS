"""HTTP request middleware, context processors, and session lifecycle hooks."""

import time
from flask import g, request, session
from core.database import close_session


def register_middleware(app):
    """Register core request and response hooks on the Flask application."""

    @app.before_request
    def before_request_hook():
        g.start_time = time.time()
        g.user_id = session.get("user_id")
        g.user_role = session.get("user_role")
        g.user_name = session.get("user_name")
        g.user_email = session.get("user_email")

    @app.after_request
    def after_request_hook(response):
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time
            response.headers["X-Response-Time"] = f"{elapsed:.4f}s"
        return response

    @app.teardown_appcontext
    def teardown_db(exception=None):
        close_session(exception)
