from collections.abc import AsyncIterator

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from orbotino.db.models import Base, Channel, OAuthToken
from orbotino.db.session import Database


@pytest.fixture
async def db() -> AsyncIterator[Database]:
    database = Database("sqlite+aiosqlite:///:memory:")
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield database
    await database.dispose()


async def test_channel_roundtrip(db: Database) -> None:
    async with db.session() as session:
        session.add(
            Channel(twitch_id="1", login="tester", display_name="Tester", overlay_token="abc")
        )
        await session.commit()

    async with db.session() as session:
        channel = await session.scalar(select(Channel).where(Channel.twitch_id == "1"))
        assert channel is not None
        assert channel.prefix == "!"


async def test_tokens_are_unique(db: Database) -> None:
    async with db.session() as session:
        session.add(OAuthToken(owner_id="1111", provider="twitch", access_token_enc="a", scopes=""))
        session.add(OAuthToken(owner_id="1111", provider="twitch", access_token_enc="b", scopes=""))
        with pytest.raises(IntegrityError, match="UNIQUE"):
            await session.commit()
