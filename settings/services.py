"""System settings management services."""

from core.database import get_session
from settings.models import SystemSetting

DEFAULT_SETTINGS = {
    "site_name": ("Enterprise LMS", "Platform title displayed across application", "general"),
    "support_email": ("support@lms.local", "Contact email address for inquiries", "general"),
    "allow_self_registration": ("true", "Enable public student account registration", "security"),
    "min_attendance_percentage": ("75.0", "Minimum attendance percentage required for course completion", "academic"),
    "default_passing_grade": ("60.0", "Default course passing threshold percentage", "academic"),
    "theme_mode": ("dark", "Default theme mode (dark / light)", "appearance"),
}


class SettingService:
    """Operations managing persistent platform settings."""

    @staticmethod
    def seed_default_settings():
        """Ensure default system settings are populated in database."""
        session = get_session()
        for key, (val, desc, cat) in DEFAULT_SETTINGS.items():
            setting = session.query(SystemSetting).filter_by(key=key).first()
            if not setting:
                setting = SystemSetting(key=key, value=val, description=desc, category=cat)
                session.add(setting)
        session.commit()

    @staticmethod
    def get_setting(key: str, default: str = "") -> str:
        """Fetch setting value by key."""
        setting = get_session().query(SystemSetting).filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_setting(key: str, value: str, description: str = None, category: str = "general") -> SystemSetting:
        """Update or insert a setting."""
        session = get_session()
        setting = session.query(SystemSetting).filter_by(key=key).first()
        if not setting:
            setting = SystemSetting(key=key, value=str(value), description=description, category=category)
            session.add(setting)
        else:
            setting.value = str(value)
            if description:
                setting.description = description
        session.commit()
        return setting

    @staticmethod
    def get_all_settings() -> dict[str, str]:
        """Fetch all settings as a key-value dictionary."""
        settings = get_session().query(SystemSetting).all()
        return {s.key: s.value for s in settings}
