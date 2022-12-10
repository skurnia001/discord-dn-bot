# bot.py
import asyncio
import logging
import logging.handlers

import discord
import os

from discord.ext.commands import Context
from dotenv import load_dotenv
from discord.ext import commands

from src.subbot.DN.DungeonKilos import DNDungeonKilos
from src.subbot.DN.ReminderEvent import DNReminderEventBot
from src.subbot.DN.STGReq import DNSTGReq
from src.subbot.DN.SkillQuery import DNSkillQuery
from src.subbot.Venti import Venti

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
master_bot = commands.Bot(command_prefix=('/',), intents=intents)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DNSkillQuery(bot))
    await bot.add_cog(Venti(bot))
    await bot.add_cog(DNReminderEventBot(bot, CHANNEL_ID))
    await bot.add_cog(DNSTGReq(bot))
    await bot.add_cog(DNDungeonKilos(bot))


@master_bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: Context) -> None:
    ctx.bot.tree.copy_global_to(guild=ctx.guild)
    synced = await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send(
        f"Synced {len(synced)} commands"
    )


async def main() -> None:
    await setup(master_bot)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='log/discord.log',
        encoding='utf-8',
        maxBytes=4 * 1024 * 1024,  # 1 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with master_bot:
        print("Bot started...")
        await master_bot.start(TOKEN)


asyncio.run(main())
