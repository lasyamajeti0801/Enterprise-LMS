"""Internal event listener and dispatcher for decoupling audit logs and notifications."""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Publish-subscribe event bus for decoupled domain event handling."""

    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, handler):
        """Register a callable handler for a specific event type."""
        self._subscribers[event_type].append(handler)

    def emit(self, event_type: str, **kwargs):
        """Trigger all registered handlers for the given event type."""
        for handler in self._subscribers.get(event_type, []):
            try:
                handler(**kwargs)
            except Exception as e:
                logger.error(f"Error handling event '{event_type}' with handler {handler}: {e}", exc_info=True)


events = EventDispatcher()
