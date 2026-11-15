import time
from collections.abc import Callable


class CooldownManager:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        # key: (channel_id, command_name, user_id or None for the global cooldown)
        # value: when it was last used (a clock() value, in seconds)
        self._last_used: dict[tuple[str, str, str | None], float] = {}

    def remaining(
        self,
        channel_id: str,
        command: str,
        user_id: str,
        global_cooldown: float,
        user_cooldown: float,
    ) -> float:
        now = self._clock()  # get current time
        global_left = self._left((channel_id, command, None), global_cooldown, now)
        user_left = self._left((channel_id, command, user_id), user_cooldown, now)
        return max(global_left, user_left, 0.0)

    def _left(self, key: tuple[str, str, str | None], cooldown: float, now: float) -> float:
        last_used = self._last_used.get(key)
        if last_used is None:
            return 0.0
        return cooldown - (now - last_used)

    def record(self, channel_id: str, command: str, user_id: str) -> None:
        now = self._clock()
        self._last_used[channel_id, command, None] = now
        self._last_used[channel_id, command, user_id] = now
