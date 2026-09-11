"""Dynamic system configuration and preference storage models."""

from sqlalchemy import Column, String, Text
from core.database import Base, ModelMixin


class SystemSetting(Base, ModelMixin):
    """Dynamic key-value system configuration."""

    __tablename__ = "system_settings"

    key = Column(String(64), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(32), default="general", nullable=False)  # general, academic, security, appearance

    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
