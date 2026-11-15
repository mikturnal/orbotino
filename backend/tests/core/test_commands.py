import pytest

from orbotino.core.commands import Command, CommandContext, CommandRegistry, Permission
from orbotino.core.cooldowns import CooldownManager
from orbotino.core.events import ChatMessage, Roles


class FakeSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str | None]] = []

    async def send_message(self, channel_id: str, text: str, reply_to: str | None = None) -> None:
        self.sent.append((channel_id, text, reply_to))


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def sender() -> FakeSender:
    return FakeSender()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def registry(sender: FakeSender, clock: FakeClock) -> CommandRegistry:
    return CommandRegistry(sender, CooldownManager(clock=clock))


NO_ROLES = Roles()


def make_message(text: str, roles: Roles = NO_ROLES) -> ChatMessage:
    return ChatMessage(
        channel_id="channel1",
        message_id="msg1",
        user_id="user1",
        user_login="viewer",
        display_name="Viewer",
        text=text,
        roles=roles,
    )


async def reply_pong(ctx: CommandContext) -> None:
    await ctx.reply("pong")


async def reply_args(ctx: CommandContext) -> None:
    await ctx.reply(ctx.args)


async def test_command_reply_gets_sent(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="ping", handler=reply_pong))

    await registry.handle(make_message("!ping"))

    assert sender.sent == [("channel1", "pong", "msg1")]


async def test_alias_triggers_command(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="ping", handler=reply_pong, aliases=("also_ping",)))

    await registry.handle(make_message("!also_ping"))

    assert sender.sent == [("channel1", "pong", "msg1")]


async def test_uppercase_commands_work(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="ping", handler=reply_pong))

    await registry.handle(make_message("!PING"))

    assert sender.sent == [("channel1", "pong", "msg1")]


async def test_no_prefix_or_unknown_do_nothing(
    registry: CommandRegistry, sender: FakeSender
) -> None:
    registry.register(Command(name="ping", handler=reply_pong))

    await registry.handle(make_message("ping"))
    await registry.handle(make_message("!pling"))

    assert sender.sent == []


async def test_moderator_only_command(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="ping", handler=reply_pong, permission=Permission.MODERATOR))

    await registry.handle(make_message("!ping"))
    assert sender.sent == []

    await registry.handle(make_message("!ping", Roles(moderator=True)))
    assert sender.sent == [("channel1", "pong", "msg1")]


async def test_cooldown_blocks_until_expired(
    registry: CommandRegistry, sender: FakeSender, clock: FakeClock
) -> None:
    registry.register(Command(name="ping", handler=reply_pong, user_cooldown=30))

    await registry.handle(make_message("!ping"))
    await registry.handle(make_message("!ping"))
    assert len(sender.sent) == 1

    clock.now += 31
    await registry.handle(make_message("!ping"))
    assert len(sender.sent) == 2


async def test_moderator_bypasses_cooldown(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="ping", handler=reply_pong, user_cooldown=30))
    mod = Roles(moderator=True)

    await registry.handle(make_message("!ping", mod))
    await registry.handle(make_message("!ping", mod))

    assert len(sender.sent) == 2


def test_duplicate_name_raises_error(registry: CommandRegistry) -> None:
    registry.register(Command(name="ping", handler=reply_pong))

    with pytest.raises(ValueError):
        registry.register(Command(name="ping", handler=reply_pong))

    with pytest.raises(ValueError):
        registry.register(Command(name="pong", handler=reply_pong, aliases=("ping",)))


def test_permission_of_returns_highest_role() -> None:
    assert Permission.of(Roles()) == Permission.EVERYONE
    assert Permission.of(Roles(subscriber=True)) == Permission.SUBSCRIBER
    assert Permission.of(Roles(subscriber=True, moderator=True)) == Permission.MODERATOR
    assert Permission.of(Roles(broadcaster=True, moderator=True)) == Permission.BROADCASTER


async def test_handler_receives_args(registry: CommandRegistry, sender: FakeSender) -> None:
    registry.register(Command(name="echo", handler=reply_args))

    await registry.handle(make_message("!echo hello world"))

    assert sender.sent == [("channel1", "hello world", "msg1")]
