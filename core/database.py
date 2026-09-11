"""Database connection and SQLAlchemy 2.0 declarative base setup."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()
_engine = None
_session_factory = None
db_session = None


def get_utc_now():
    """Return current UTC datetime (naive for SQLite/SQLAlchemy compatibility)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ModelMixin:
    """Base mixin providing common database columns, methods, and serialization."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    def to_dict(self):
        """Serialize model instance columns into a dictionary."""
        result = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            result[column.name] = val
        return result

    def save(self):
        """Persist current instance to the active database session."""
        session = get_session()
        session.add(self)
        session.commit()
        return self

    def delete(self):
        """Delete current instance from the active database session."""
        session = get_session()
        session.delete(self)
        session.commit()


def import_all_models():
    """Import all domain models to ensure complete SQLAlchemy relationship mapping."""
    try:
        import roles.models
        import users.models
        import students.models
        import instructors.models
        import authentication.models
        import courses.models
        import modules.models
        import lessons.models
        import materials.models
        import enrollment.models
        import progress.models
        import attendance.models
        import question_bank.models
        import quizzes.models
        import examinations.models
        import assignments.models
        import submissions.models
        import grading.models
        import certificates.models
        import gamification.models
        import skills.models
        import discussions.models
        import notifications.models
        import calendar_events.models
        import audit.models
        import settings.models
    except Exception:
        pass


def init_db(database_uri="sqlite:///lms_dev.db", echo=False):
    """Initialize database engine, create all tables, and establish session factory."""
    global _engine, _session_factory, db_session

    import_all_models()

    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(database_uri, echo=echo, connect_args=connect_args)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    db_session = scoped_session(_session_factory)

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=_engine)
    return _engine


def get_session():
    """Get the thread-local scoped database session."""
    global db_session
    if db_session is None:
        init_db()
    return db_session


def close_session(exception=None):
    """Remove active database session at the end of request lifecycle."""
    global db_session
    if db_session is not None:
        db_session.remove()
