import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from orbotino.core.events import Event

logger = logging.getLogger(__name__)

type Handler[E: Event] = Callable[[E], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[type[Event], list[Handler[Any]]] = defaultdict(list)
        self._tasks: set[asyncio.Task[None]] = set()

    def subscribe[E: Event](self, event_type: type[E], handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers[type(event)]:
            task = asyncio.create_task(self._run(handler, event))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def drain(self) -> None:
        while self._tasks:
            await asyncio.gather(*list(self._tasks))

    async def _run(self, handler: Handler[Any], event: Event) -> None:
        try:
            await handler(event)
        except Exception:
            name = getattr(handler, "__qualname__", repr(handler))
            logger.exception("Handler %s failed for %s", name, type(event).__name__)
