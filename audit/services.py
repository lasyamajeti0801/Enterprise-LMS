"""Audit trail logging and query services."""

import json
from core.database import get_session, get_utc_now
from core.pagination import paginate_query
from audit.models import AuditLog


class AuditService:
    """Operations recording immutable system operations and changes."""

    @staticmethod
    def log_action(
        action: str,
        entity_type: str,
        entity_id: str = None,
        user_id: int = None,
        old_values: dict = None,
        new_values: dict = None,
        ip_address: str = "127.0.0.1",
        status: str = "SUCCESS",
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        session = get_session()
        log_entry = AuditLog(
            action=action.upper(),
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            user_id=user_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            timestamp=get_utc_now(),
            status=status.upper(),
        )
        session.add(log_entry)
        session.commit()
        return log_entry

    @staticmethod
    def get_logs(action: str = "", entity_type: str = "", user_id: int = None, page: int = 1, per_page: int = 20):
        """Retrieve paginated audit logs with search filters."""
        query = get_session().query(AuditLog)
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
        query = query.order_by(AuditLog.timestamp.desc())
        return paginate_query(query, page=page, per_page=per_page)
