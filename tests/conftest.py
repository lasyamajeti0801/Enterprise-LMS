"""Pytest fixtures and test database isolation."""

import pytest
from app import create_app
from config.settings import TestingConfig
from core.database import Base, close_session, get_session, init_db
from gamification.services import GamificationService
from roles.services import RoleService
from settings.services import SettingService
from users.services import UserService


@pytest.fixture(scope="session")
def app():
    """Create testing application context."""
    app = create_app(config_class=TestingConfig)
    return app


@pytest.fixture(scope="function")
def db_session(app):
    """Provide isolated in-memory test database session per test."""
    with app.app_context():
        engine = init_db("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        RoleService.seed_default_roles_and_permissions()
        SettingService.seed_default_settings()
        GamificationService.seed_default_badges()

        session = get_session()
        yield session

        close_session()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app, db_session):
    """Provide HTTP test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_admin(db_session):
    """Create sample administrator user."""
    return UserService.create_user(
        username="test_admin",
        email="test_admin@lms.local",
        password="adminpassword123",
        first_name="Admin",
        last_name="User",
        role_name="admin",
    )


@pytest.fixture
def sample_instructor(db_session):
    """Create sample instructor with profile."""
    from instructors.services import InstructorService
    user = UserService.create_user(
        username="test_instructor",
        email="test_inst@lms.local",
        password="instpassword123",
        first_name="Prof",
        last_name="Turing",
        role_name="instructor",
    )
    profile = InstructorService.create_or_get_profile(user.id)
    return user, profile


@pytest.fixture
def sample_student(db_session):
    """Create sample student with profile."""
    from students.services import StudentService
    user = UserService.create_user(
        username="test_student",
        email="test_std@lms.local",
        password="stdpassword123",
        first_name="Alice",
        last_name="Wong",
        role_name="student",
    )
    profile = StudentService.create_or_get_profile(user.id)
    return user, profile
