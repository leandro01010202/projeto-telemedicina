import asyncio
import logging
from typing import Callable, Any
from collections import defaultdict

from events.events import Event

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._handlers: dict[type[Event], list[Callable]] = defaultdict(list)
        self._async_handlers: dict[type[Event], list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type[Event], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def subscribe_async(self, event_type: type[Event], handler: Callable) -> None:
        self._async_handlers[event_type].append(handler)

    def on(self, event_type: type[Event]):
        def decorator(func: Callable):
            if asyncio.iscoroutinefunction(func):
                self.subscribe_async(event_type, func)
            else:
                self.subscribe(event_type, func)
            return func
        return decorator

    async def publish(self, event: Event) -> None:
        event_type = type(event)
        logger.info(f"Publicando evento: {event_type.__name__}")

        # Handlers síncronos
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Erro no handler {handler.__name__}: {e}")

        # Handlers assíncronos
        for handler in self._async_handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Erro no handler assíncrono {handler.__name__}: {e}")

    def clear(self) -> None:
        self._handlers.clear()
        self._async_handlers.clear()


event_bus = EventBus()
