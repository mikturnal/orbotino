import asyncio

import pytest

from orbotino.core.bus import EventBus
from orbotino.core.events import ChatMessage, StreamOnline


def make_message(text: str = "Hello World!") -> ChatMessage:
    return ChatMessage(
        channel_id="1",
        message_id="1",
        user_id="user1",
        user_login="login",
        display_name="testuser",
        text=text,
    )


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


async def test_handler_receives_published_event(bus: EventBus) -> None:
    received: list[ChatMessage] = []

    async def handler(event: ChatMessage) -> None:
        received.append(event)

    bus.subscribe(ChatMessage, handler)
    message = make_message()
    bus.publish(message)
    await bus.drain()

    assert received == [message]


async def test_handler_only_receives_subscribed_event(bus: EventBus) -> None:
    received: list[StreamOnline] = []

    async def handler(event: StreamOnline) -> None:
        received.append(event)

    bus.subscribe(StreamOnline, handler)
    message = make_message()
    bus.publish(message)
    await bus.drain()

    assert received == []


async def test_multiple_handlers_receive_published_event(bus: EventBus) -> None:
    received_1: list[ChatMessage] = []
    received_2: list[ChatMessage] = []

    async def handler_1(event: ChatMessage) -> None:
        received_1.append(event)

    async def handler_2(event: ChatMessage) -> None:
        received_2.append(event)

    bus.subscribe(ChatMessage, handler_1)
    bus.subscribe(ChatMessage, handler_2)
    message = make_message()
    bus.publish(message)
    await bus.drain()

    assert received_1 == [message]
    assert received_2 == [message]


async def test_failing_handler_gets_handled(
    bus: EventBus, caplog: pytest.LogCaptureFixture
) -> None:
    received_1: list[ChatMessage] = []

    async def handler_1(event: ChatMessage) -> None:
        received_1.append(event)

    async def handler_2(event: ChatMessage) -> None:
        raise RuntimeError("This is a RuntimeError.")

    bus.subscribe(ChatMessage, handler_1)
    bus.subscribe(ChatMessage, handler_2)
    message = make_message()
    bus.publish(message)
    await bus.drain()

    assert received_1 == [message]
    assert "This is a RuntimeError." in caplog.text


async def test_publish_returns_before_handlers_finish(bus: EventBus) -> None:
    received: list[ChatMessage] = []

    async def handler(event: ChatMessage) -> None:
        await asyncio.sleep(0.1)
        received.append(event)

    bus.subscribe(ChatMessage, handler)
    message = make_message()
    bus.publish(message)
    assert received == []

    await bus.drain()

    assert received == [message]
