# bot.py
import asyncio
import datetime
import logging
import logging.handlers
from typing import Literal

import discord
from dateutil import relativedelta
import difflib
import os
import string

import pymongo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Context
from dotenv import load_dotenv
from discord.ext import commands
import pandas as pd

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DB_UNAME = os.getenv('DB_UNAME')
DB_PWD = os.getenv('DB_PWD')
DB_URL = os.getenv('DB_URL')

intents = discord.Intents.default()
intents.message_content = True
master_bot = commands.Bot(command_prefix=('/',), intents=intents)


class DNSTGReq(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.df = pd.read_csv('stg_req.csv')
        self.df = self.df.set_index('Floor')
        self.stg_min = min(self.df.index)
        self.stg_max = max(self.df.index)
        self.prefix = '/'
        self.command_mapper = {
            'cdmg': ['CDM Cap', 'CDM Penalty', 'CDM % Cap'],
            'cdm': ['CDM Cap', 'CDM Penalty', 'CDM % Cap'],
            'crit': ['Crit Cap', 'Crit Penalty', 'Crit % Cap'],
            'def': ['Pdef/Mdef Cap', 'Pdef/Mdef Penalty', 'Pdef/Mdef % Cap'],
            'mdef': ['Pdef/Mdef Cap', 'Pdef/Mdef Penalty', 'Pdef/Mdef % Cap'],
            'fd': ['FD Cap', 'FD Penalty', 'FD % Cap'],
        }

    @commands.hybrid_command(name='stgreq', aliases=['crit', 'cdmg', 'cdm', 'def', 'mdef', 'fd'],
                             help='Returns the required stats given the stg requirement (13-20). ' +
                                  'Refer to the command alias for stats.')
    async def stgreq(self, ctx: commands.Context, stg: int) -> None:

        stat = self.command_mapper.get(ctx.invoked_with, self.df.columns)

        # Return error message if stg is not within range
        if stg not in range(self.stg_min, self.stg_max + 1):
            res = f"STG argument is wrong! Please enter a valid integer between {self.stg_min} and {self.stg_max}."

        # Return the stat for a given stg
        else:
            res = self.df[stat]
            if stg:
                res = res.loc[stg]
            res = res.to_string()

        command_source = ctx.invoked_with.title()
        if command_source == 'Stgreq':
            command_source = 'STG'

        await ctx.send("```\n" + f"{command_source} requirements for {stg}:\n" + res + "```\n")


class DNSkillQuery(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.df = pd.read_csv('skill.csv')
        self.prefix = '/'
        self.thresh = 0.6
        self.matcher = difflib.SequenceMatcher(lambda x: x == ' ')

    def sim_score(self, str_1: str, str_2: str) -> float:
        self.matcher.set_seqs(str_1.lower(), str_2.lower())
        return self.matcher.ratio()

    @commands.hybrid_command(name='query', aliases=['qd', 'qry'],
                             help='General query of the database, arg: col_name skill names')
    async def query(self, ctx: commands.Context, col: Literal["Equipment", "Skill", "Class"], name: str) -> None:
        tmp = self.df.copy()
        tmp['Score'] = tmp[string.capwords(col)].map(lambda x: self.sim_score(x, name))
        tmp.sort_values('Score', inplace=True, ascending=False)
        res = tmp[tmp['Score'] > self.thresh]
        await ctx.send("```\n" + res.to_string() + "```\n")

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.prefix == self.prefix

    @commands.hybrid_command(name='jsq', aliases=['jadeskillquery', ],
                             help='Finds a class whose skill match the skill name given.')
    async def jsq(self, ctx: commands.Context, name: str) -> None:
        await self.query(ctx, 'skill', name)

    @commands.hybrid_command(name='esq', aliases=['eqskillquery', ],
                             help='Finds a class whose skill is in the equipment name given.')
    async def esq(self, ctx: commands.Context, name: str) -> None:
        await self.query(ctx, 'equipment', name)


class Venti(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.prefix = 'ehe'

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.prefix == self.prefix

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == master_bot.user:
            return
        if "ehe" in message.content.lower():
            await message.channel.send("EHE TE NANDAYO")

    # @commands.command(name='')
    # async def ehe(self, ctx, *args):
    #     if ctx.author == bot.user:
    #         return
    #     # if "ehe" in ctx.message:
    #     await ctx.send("EHE TE NANDAYO")


class DNReminderEventBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.reminder_callback, CronTrigger(hour="0, 18, 21, 23"))
        self.scheduler.start()
        connection_string = f"mongodb+srv://{DB_UNAME}:{DB_PWD}@{DB_URL}/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.dn_event_db.dn_event_db

    def get_event_from_db(self, mode: str = "current") -> pd.DataFrame:
        arr = []
        query_dic = {}
        if mode == "current":
            query_dic = {
                "start_date": {"$lt": datetime.datetime.now()},
                "end_date": {"$gt": datetime.datetime.now()}
            }
        else:
            curdate = datetime.datetime.now()
            query_dic = {
                "start_date": {"$gt": (curdate.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)},
                "end_date": {"$lt": curdate + relativedelta.relativedelta(day=31)}
            }
        for row in self.db.find(query_dic):
            del row['_id']
            row['start_date'] = row['start_date'].strftime('%Y-%m-%d %H:%M:%S')
            row['end_date'] = row['end_date'].strftime('%Y-%m-%d %H:%M:%S')
            arr.append(row)
        res_df = pd.DataFrame(arr)
        if len(arr) != 0:  # TODO: STUPID HOTFIX
            res_df.columns = ["Event Name", "Event Description", "Start Date", "End Date"]
        return res_df

    async def reminder_callback(self) -> None:
        c = master_bot.get_channel(CHANNEL_ID)
        res_df = self.get_event_from_db()
        if len(res_df) > 0:
            await c.send("```\n" + res_df.to_string() + "\n```")

    @commands.hybrid_command(name="qev", aliases=['queryevent', 'qevent'],
                             help="Get all events")
    async def query_event(self, ctx: commands.Context, mode: Literal["current", "all"] = "current") -> None:
        res_df = self.get_event_from_db(mode)
        await ctx.send("```\n" + res_df.to_string() + "\n```")

    @commands.hybrid_command(name='addev', aliases=['addevent'],
                             help="Add event to be reminded daily")
    async def add_event(
            self,
            ctx: commands.Context,
            event_name: str,
            start_year: int,
            start_month: int,
            start_day: int,
            end_year: int,
            end_month: int,
            end_day: int,
            event_desc: str = ''):
        start_date = datetime.datetime(start_year, start_month, start_day)
        end_date = datetime.datetime(end_year, end_month, end_day, 23, 59, 59)
        obj_dic = {
            "event_name": event_name,
            "event_desc": event_desc,
            "start_date": start_date,
            "end_date": end_date
        }
        self.db.insert_one(obj_dic)
        await ctx.send("event recorded")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DNSkillQuery(bot))
    await bot.add_cog(Venti(bot))
    await bot.add_cog(DNReminderEventBot(bot))
    await bot.add_cog(DNSTGReq(bot))


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
