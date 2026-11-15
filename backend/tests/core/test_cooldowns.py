from orbotino.core.cooldowns import CooldownManager


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_unused_command_has_no_cooldown() -> None:
    cooldowns = CooldownManager(clock=FakeClock())

    left = cooldowns.remaining("channel1", "sr", "user1", global_cooldown=30, user_cooldown=60)

    assert left == 0.0


def test_user_cooldown_only_for_that_user() -> None:
    cooldowns = CooldownManager(clock=FakeClock())

    cooldowns.record("channel1", "sr", "user1")

    left_1 = cooldowns.remaining("channel1", "sr", "user1", global_cooldown=0, user_cooldown=60)
    left_2 = cooldowns.remaining("channel1", "sr", "user2", global_cooldown=0, user_cooldown=60)

    assert left_1 == 60.0
    assert left_2 == 0.0


def test_cooldown_passed_after_time_passed() -> None:
    clock = FakeClock()
    cooldowns = CooldownManager(clock=clock)

    cooldowns.record("channel1", "sr", "user1")
    clock.now += 60

    left_1 = cooldowns.remaining("channel1", "sr", "user1", global_cooldown=30, user_cooldown=60)
    assert left_1 == 0.0


def test_global_cooldown_for_all_users() -> None:
    cooldowns = CooldownManager(clock=FakeClock())

    cooldowns.record("channel1", "sr", "user1")

    left_1 = cooldowns.remaining("channel1", "sr", "user1", global_cooldown=30, user_cooldown=0)
    left_2 = cooldowns.remaining("channel1", "sr", "user2", global_cooldown=30, user_cooldown=0)

    assert left_1 == 30.0
    assert left_2 == 30.0
