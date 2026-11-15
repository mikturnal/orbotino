import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol

from orbotino.core.cooldowns import CooldownManager
from orbotino.core.events import ChatMessage, Roles

logger = logging.getLogger(__name__)


class ChatSender(Protocol):
    async def send_message(
        self, channel_id: str, text: str, reply_to: str | None = None
    ) -> None: ...


class Permission(IntEnum):
    EVERYONE = 0
    SUBSCRIBER = 1
    VIP = 2
    MODERATOR = 3
    BROADCASTER = 4

    @classmethod
    def of(cls, roles: Roles) -> "Permission":
        if roles.broadcaster:
            return cls.BROADCASTER
        if roles.moderator:
            return cls.MODERATOR
        if roles.vip:
            return cls.VIP
        if roles.subscriber:
            return cls.SUBSCRIBER
        return cls.EVERYONE


type CommandHandler = Callable[[CommandContext], Awaitable[None]]


@dataclass(frozen=True, slots=True, kw_only=True)
class Command:
    name: str
    handler: CommandHandler
    aliases: tuple[str, ...] = ()
    help: str = ""
    permission: Permission = Permission.EVERYONE
    global_cooldown: float = 0.0
    user_cooldown: float = 0.0


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandContext:
    message: ChatMessage
    command: Command
    args: str
    sender: ChatSender

    async def reply(self, text: str) -> None:
        await self.sender.send_message(
            self.message.channel_id, text, reply_to=self.message.message_id
        )


class CommandRegistry:
    def __init__(self, sender: ChatSender, cooldowns: CooldownManager, prefix: str = "!") -> None:
        self._sender = sender
        self._cooldowns = cooldowns
        self._prefix = prefix
        self._commands: dict[str, Command] = {}  # name AND every alias → command

    def register(self, command: Command) -> None:
        names = [command.name.lower(), *(alias.lower() for alias in command.aliases)]
        for name in names:
            if name in self._commands:
                raise ValueError(f"Command name {name!r} is already registered")
        for name in names:
            self._commands[name] = command

    def commands(self) -> list[Command]:
        return sorted(set(self._commands.values()), key=lambda c: c.name)

    async def handle(self, message: ChatMessage) -> None:
        # no prefix
        if not message.text.startswith(self._prefix):
            return

        # only prefix
        parts = message.text[len(self._prefix) :].split(maxsplit=1)
        if not parts:
            return
        name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # unknown command
        command = self._commands.get(name)
        if command is None:
            return

        # permission level
        level = Permission.of(message.roles)
        if level < command.permission:
            logger.debug("%s lacks permission for !%s", message.user_login, command.name)
            return

        # cooldown
        if level < Permission.MODERATOR:
            remaining = self._cooldowns.remaining(
                message.channel_id,
                command.name,
                message.user_id,
                command.global_cooldown,
                command.user_cooldown,
            )
            if remaining > 0:
                logger.debug(
                    "!%s on cooldown for %s (%.0fs)", command.name, message.user_login, remaining
                )
                return

        self._cooldowns.record(message.channel_id, command.name, message.user_id)
        context = CommandContext(message=message, command=command, args=args, sender=self._sender)
        await command.handler(context)
