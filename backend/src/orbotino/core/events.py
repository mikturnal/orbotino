from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class Event:
    """Base class for everything that can be published on the EventBus."""

    channel_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Roles:
    broadcaster: bool = False
    moderator: bool = False
    vip: bool = False
    subscriber: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class ChatMessage(Event):
    message_id: str
    user_id: str
    user_login: str
    display_name: str
    text: str
    roles: Roles = Roles()
    reply_to_message_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class StreamOnline(Event):
    """Stream startet."""

    started_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class StreamOffline(Event):
    """Stream ended. Only inherits channel_id."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ChannelUpdate(Event):
    title: str
    category: str
