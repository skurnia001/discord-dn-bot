#!/usr/bin/env python
# bot.py
import asyncio
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
from src.utils.logger import setup_logger

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

async def main() -> None:
    logger = setup_logger()

    # Load Config 
    config=dict()
    try:
        with open("config.yaml", "r") as stream:
            config= yaml.safe_load(stream)
    except FileNotFoundError or yaml.YAMLError as exc:
        logger.warning(f"Unable to load config file. Reverting to default... Error is {exc}")
    if 'DisabledServices' not in config:
        config['DisabledServices']=list()

    await setup(master_bot, config)

    async with master_bot:
        logger.info("Bot started...")
        await master_bot.start(TOKEN)


asyncio.run(main())
