import pytest_asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest

from src.subbot.Venti import Venti


@pytest_asyncio.fixture
async def bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix=('/',), intents=intents)

    await b._async_setup_hook()
    await b.add_cog(Venti(b))

    dpytest.configure(b)
    return b


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    yield
    await dpytest.empty_queue()
