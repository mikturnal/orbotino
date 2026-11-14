import pytest

from orbotino.core.settings import Settings

REQUIRED = {
    "SECRET_KEY": "test-secret",
    "TOKEN_ENCRYPTION_KEY": "test-key",
    "TWITCH_CLIENT_ID": "twitch-client-id",
    "TWITCH_CLIENT_SECRET": "twitch-client-secret",
    "TWITCH_BOT_ID": "bot-id",
    "TWITCH_OWNER_ID": "owner-id",
    "DISCORD_TOKEN": "discord-token",
    "SPOTIFY_CLIENT_ID": "spotify-client-id",
    "SPOTIFY_CLIENT_SECRET": "spotify-client-secret",
}


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Sets all required variables for one test; undone automatically afterwards."""
    for name, value in REQUIRED.items():
        monkeypatch.setenv(name, value)
    return monkeypatch


@pytest.fixture
def settings(env: pytest.MonkeyPatch) -> Settings:
    """A Settings object built only from the test variables, never the real .env."""
    return Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
