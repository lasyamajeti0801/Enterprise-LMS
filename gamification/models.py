"""Gamification domain models: Experience Points (XP), Badges, and Streaks."""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base, ModelMixin, get_utc_now


class UserPoints(Base, ModelMixin):
    """Tracks XP, levels, and consecutive learning streak days for a user."""

    __tablename__ = "user_points"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_xp = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    current_streak_days = Column(Integer, default=1, nullable=False)
    last_activity_date = Column(Date, nullable=True)

    user = relationship("User")

    def __repr__(self):
        return f"<UserPoints User:{self.user_id} XP:{self.total_xp} Lvl:{self.current_level}>"


class Badge(Base, ModelMixin):
    """Unlockable achievement badge."""

    __tablename__ = "badges"

    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(255), nullable=False)
    icon_name = Column(String(64), default="award", nullable=False)
    xp_reward = Column(Integer, default=100, nullable=False)

    users = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Badge {self.code}: {self.name}>"


class UserBadge(Base, ModelMixin):
    """Association of badges earned by a user."""

    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), index=True, nullable=False)
    awarded_at = Column(DateTime, default=get_utc_now, nullable=False)

    badge = relationship("Badge", back_populates="users")
    user = relationship("User")

    def __repr__(self):
        return f"<UserBadge User:{self.user_id} Badge:{self.badge_id}>"
