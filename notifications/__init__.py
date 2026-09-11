"""Notifications package initialization."""

from notifications.models import Notification
from notifications.services import NotificationService

__all__ = ["Notification", "NotificationService"]
