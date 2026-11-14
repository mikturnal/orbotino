import asyncio
import logging

import pytest

from orbotino.app import Application
from orbotino.core.settings import Settings


async def test_run_stops_when_requested(settings: Settings) -> None:
    app = Application(settings)

    task = asyncio.create_task(app.run(install_signal_handlers=False))
    await asyncio.sleep(0)

    app.request_stop()

    await asyncio.wait_for(task, timeout=1)
    assert task.done()


async def test_stop_is_logged(settings: Settings, caplog: pytest.LogCaptureFixture) -> None:
    app = Application(settings)
    caplog.set_level(logging.INFO)

    task = asyncio.create_task(app.run(install_signal_handlers=False))
    await asyncio.sleep(0)

    app.request_stop()

    await asyncio.wait_for(task, timeout=1)
    assert "stopped" in caplog.text
