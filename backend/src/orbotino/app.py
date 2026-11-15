import asyncio
import logging
import signal

from orbotino.core.bus import EventBus
from orbotino.core.settings import Settings
from orbotino.db.session import Database

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._stop_event = asyncio.Event()
        self.db = Database(self.settings.database_url)
        self.bus = EventBus()

    def request_stop(self) -> None:
        logger.info("Stop requested!")
        self._stop_event.set()

    async def start(self) -> None:
        logger.info("orbotino starting in %s mode", self.settings.orbotino_env)
        # startup code

    async def stop(self) -> None:
        logger.info("orbotino stopping")
        # shutdown code
        await self.db.dispose()
        await self.bus.drain()
        logger.info("orbotino stopped")

    async def run(self, install_signal_handlers: bool = True) -> None:
        if install_signal_handlers:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self.request_stop)

        await self.start()
        try:
            await self._stop_event.wait()
        finally:
            await self.stop()
