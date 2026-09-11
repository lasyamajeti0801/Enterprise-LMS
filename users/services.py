"""User management and query services."""

from datetime import timedelta
from sqlalchemy import or_
from core.database import get_session, get_utc_now
from core.exceptions import ResourceNotFoundError, ValidationError
from core.pagination import paginate_query
from core.security import hash_password
from core.validators import validate_email, validate_username
from roles.models import Role
from users.models import User


class UserService:
    """Enterprise user management operations."""

    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role_name: str = "student",
        phone_number: str = None,
        bio: str = None,
        status: str = "active",
    ) -> User:
        """Create a new user with validation and proper role association."""
        session = get_session()

        username = username.strip()
        email = email.strip().lower()

        if not validate_username(username):
            raise ValidationError("Invalid username format. Must be 3-30 alphanumeric characters.")
        if not validate_email(email):
            raise ValidationError("Invalid email address format.")

        # Check duplicates
        if session.query(User).filter_by(username=username).first():
            raise ValidationError(f"Username '{username}' is already taken.")
        if session.query(User).filter_by(email=email).first():
            raise ValidationError(f"Email '{email}' is already registered.")

        role = session.query(Role).filter_by(name=role_name.lower()).first()
        if not role:
            raise ValidationError(f"Specified role '{role_name}' does not exist.")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role_id=role.id,
            phone_number=phone_number,
            bio=bio,
            status=status,
            is_active=(status == "active"),
        )
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Get user by primary key ID."""
        user = get_session().query(User).filter_by(id=user_id).first()
        if not user:
            raise ResourceNotFoundError(f"User with ID {user_id} not found.")
        return user

    @staticmethod
    def get_by_identifier(identifier: str) -> User | None:
        """Find user by username or email."""
        clean_id = identifier.strip().lower()
        return (
            get_session()
            .query(User)
            .filter(or_(User.username.ilike(clean_id), User.email.ilike(clean_id)))
            .first()
        )

    @staticmethod
    def update_user(user_id: int, **kwargs) -> User:
        """Update user profile information."""
        session = get_session()
        user = UserService.get_by_id(user_id)

        allowed_fields = {"first_name", "last_name", "phone_number", "bio", "avatar_url", "status"}
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        if "status" in kwargs:
            user.is_active = (user.status == "active")

        if "role_name" in kwargs and kwargs["role_name"]:
            role = session.query(Role).filter_by(name=kwargs["role_name"].lower()).first()
            if role:
                user.role_id = role.id

        session.commit()
        return user

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        session = get_session()
        user = UserService.get_by_id(user_id)
        user.password_hash = hash_password(new_password)
        user.failed_attempts = 0
        user.locked_until = None
        session.commit()
        return True

    @staticmethod
    def search_users(query_str: str = "", role_name: str = "", status: str = "", page: int = 1, per_page: int = 15):
        """Search and filter users with pagination."""
        query = get_session().query(User).join(Role)

        if query_str:
            term = f"%{query_str.strip()}%"
            query = query.filter(
                or_(
                    User.username.ilike(term),
                    User.email.ilike(term),
                    User.first_name.ilike(term),
                    User.last_name.ilike(term),
                )
            )

        if role_name:
            query = query.filter(Role.name == role_name.lower())

        if status:
            query = query.filter(User.status == status.lower())

        query = query.order_by(User.id.desc())
        return paginate_query(query, page=page, per_page=per_page)

    @staticmethod
    def count_by_role(role_name: str) -> int:
        """Count active users in a specific role."""
        return (
            get_session()
            .query(User)
            .join(Role)
            .filter(Role.name == role_name.lower())
            .count()
        )
