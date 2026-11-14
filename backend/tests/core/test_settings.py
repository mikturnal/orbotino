import pytest
from pydantic import SecretStr, ValidationError

from orbotino.core.settings import Settings


def make_settings() -> Settings:
    return Settings(_env_file=None)  # pyright: ignore[reportCallIssue]


def test_loads_required_values(env: pytest.MonkeyPatch) -> None:
    settings = make_settings()
    assert settings.twitch_client_id == "twitch-client-id"
    assert isinstance(settings.secret_key, SecretStr)
    assert settings.secret_key.get_secret_value() == "test-secret"


def test_missing_required_value_fails(env: pytest.MonkeyPatch) -> None:
    env.delenv("DISCORD_TOKEN")
    with pytest.raises(ValidationError, match="discord_token"):
        make_settings()


def test_invalid_env_value_fails(env: pytest.MonkeyPatch) -> None:
    env.setenv("ORBOTINO_ENV", "prod")
    with pytest.raises(ValidationError, match="orbotino_env"):
        make_settings()


def test_secret_is_hidden_when_printed(env: pytest.MonkeyPatch) -> None:
    settings = make_settings()
    assert "discord-token" not in str(settings.discord_token)
    assert "discord-token" not in repr(settings.discord_token)


def test_defaults(env: pytest.MonkeyPatch) -> None:
    settings = make_settings()
    assert settings.orbotino_env == "development"
    assert settings.log_level == "INFO"
