#!/usr/bin/env python
# bot.py
import asyncio
import logging
import logging.handlers
import sys
import yaml

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


async def setup(bot: commands.Bot, config: dict) -> None:
    logger = setup_logger('bot_setup')
    if not 'DNSkillQuery' in config['DisabledServices']:
        await bot.add_cog(DNSkillQuery(bot))
        logger.info("DNSkillQuery module added successfully")
    
    if not 'Venti' in config['DisabledServices']:
        await bot.add_cog(Venti(bot))
        logger.info("Venti module added successfully")
    
    if not 'DNReminderEventBot' in config['DisabledServices']:
        await bot.add_cog(DNReminderEventBot(bot, CHANNEL_ID))
        logger.info("DNReminderEventBot module added successfully")    

    if not 'DNSTGReq' in config['DisabledServices']:
        await bot.add_cog(DNSTGReq(bot))
        logger.info("DNSTGReq module added successfully")    

    if not 'DNDungeonKilos' in config['DisabledServices']:
        await bot.add_cog(DNDungeonKilos(bot))
        logger.info("DNDungeonKilos module added successfully")    


@master_bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: Context) -> None:
    ctx.bot.tree.copy_global_to(guild=ctx.guild)
    synced = await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send(
        f"Synced {len(synced)} commands"
    )


# Logger setup 
def setup_logger(name='discord') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    file_handler = logging.handlers.RotatingFileHandler(
        filename='log/discord.log',
        encoding='utf-8',
        maxBytes=4 * 1024 * 1024,  # 1 MiB
        backupCount=5,  # Rotate through 5 files
    )
    file_handler.setFormatter(formatter)

    console_handler = (logging.StreamHandler(sys.stdout)) # Mirror logs to stdout for journalctl to catch and for debugging
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

async def main() -> None:
    logger = setup_logger()

    # Load Config 
    config=dict()
    try:
        with open("config.yaml", "r") as stream:
            config= yaml.safe_load(stream)
    except FileNotFoundError or yaml.YAMLError as exc:
        logging.warning(f"Unable to load config file. Reverting to default... Error is {exc}")
    if 'DisabledServices' not in config:
        config['DisabledServices']=list()

    await setup(master_bot, config)

    async with master_bot:
        logger.info("Bot started...")
        await master_bot.start(TOKEN)


asyncio.run(main())
