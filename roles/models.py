"""Role and Permission models for enterprise RBAC."""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin

# Association table between Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base, ModelMixin):
    """Granular permission entity."""

    __tablename__ = "permissions"

    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    module = Column(String(64), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Permission {self.code}>"


class Role(Base, ModelMixin):
    """System and custom roles."""

    __tablename__ = "roles"

    name = Column(String(64), unique=True, index=True, nullable=False)
    display_name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Integer, default=0, nullable=False)  # 1 = protected system role

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, backref="roles", lazy="joined")
    users = relationship("User", back_populates="role", cascade="all, delete-orphan", lazy="select")

    def has_permission(self, permission_code: str) -> bool:
        """Check if role has a specific permission code."""
        if self.name.lower() == "admin":
            return True
        return any(p.code == permission_code for p in self.permissions)

    def __repr__(self):
        return f"<Role {self.name}>"
