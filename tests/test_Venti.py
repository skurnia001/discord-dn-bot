import pytest
import discord.ext.test as dpytest

@pytest.mark.asyncio
async def test_ping(bot):
    await dpytest.message("ehe")
    assert dpytest.verify().message().content("EHE TE NANDAYO")