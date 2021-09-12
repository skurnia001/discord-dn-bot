# bot.py
import datetime
import difflib
import logging
import os
import string

import pymongo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from discord.ext import commands
import pandas as pd

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DB_UNAME = os.getenv('DB_UNAME')
DB_PWD = os.getenv('DB_PWD')
DB_URL = os.getenv('DB_URL')

master_bot = commands.Bot(command_prefix=('/',))


class DNSTGReq(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv('stg_req.csv')
        self.df = self.df.set_index('Floor')
        self.stg_min = min(self.df.index)
        self.stg_max = max(self.df.index)
        self.prefix = '/'

    @commands.command(name='cdm', aliases=['critical_damage', 'critd' ],
                      help='Finds a class whose skill match the skill name given.')
    async def cdm(self, ctx, stg=None):
        res = self.df[['CDM Cap', 'CDM Penalty', 'CDM % Cap']]
        if stg and stg.isnumeric() and int(stg) in range(self.stg_min, self.stg_max+1):
            res = res.loc[int(stg)]
        # logging.warning(res)
        await ctx.send("```\n"+res.to_string()+"```\n")



class DNSkillQuery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv('skill.csv')
        self.prefix = '/'
        self.thresh = 0.6
        self.allowed_col = ['Equipment', 'Skill', 'Class']
        self.matcher = difflib.SequenceMatcher(lambda x: x == ' ')

    def sim_score(self, str_1, str_2):
        self.matcher.set_seqs(str_1.lower(), str_2.lower())
        return self.matcher.ratio()

    @commands.command(name='query', aliases=['qd', 'qry'],
                      help='General query of the database, arg: col_name skill names')
    async def query(self, ctx, col, *args):
        col = string.capwords(col)
        if col not in self.allowed_col:
            await ctx.send("Column selection not allowed!")
            return
        name = ' '.join(args).lower()
        tmp = self.df.copy()
        tmp['Score'] = tmp[string.capwords(col)].map(lambda x: self.sim_score(x, name))
        tmp.sort_values('Score', inplace=True, ascending=False)
        res = tmp[tmp['Score'] > self.thresh]
        await ctx.send("```\n"+res.to_string()+"```\n")

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    @commands.command(name='jsq', aliases=['jadeskillquery', ],
                      help='Finds a class whose skill match the skill name given.')
    async def jsq(self, ctx, *args):
        await self.query(ctx, 'skill', *args)

    @commands.command(name='esq', aliases=['eqskillquery', ],
                      help='Finds a class whose skill is in the equipment name given.')
    async def esq(self, ctx, *args):
        await self.query(ctx, 'equipment', *args)


class Venti(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'ehe'

    async def cog_check(self, ctx):
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
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.func, CronTrigger(hour="0, 21, 23"))
        self.scheduler.start()
        connection_string = f"mongodb+srv://{DB_UNAME}:{DB_PWD}@{DB_URL}/test?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.dn_event_db.dn_event_db

    async def func(self):
        c = master_bot.get_channel(CHANNEL_ID)
        arr = []
        query_dic = {
            "start_date": {"$lt": datetime.datetime.now()},
            "end_date": {"$gt": datetime.datetime.now()}
        }
        for row in self.db.find(query_dic):
            del row['_id']
            row['start_date'] = row['start_date'].strftime('%Y-%m-%d %H:%M:%S')
            row['end_date'] = row['end_date'].strftime('%Y-%m-%d %H:%M:%S')
            arr.append(row)
        res_df = pd.DataFrame(arr)
        if len(arr) != 0:  # TODO: STUPID HOTFIX
            res_df.columns = ["Event Name", "Event Description", "Start Date", "End Date"]
        await c.send("```\n"+res_df.to_string()+"\n```")

    # TODO: REFACTOR
    @commands.command(name="qev", aliases=['queryevent', 'qevent'],
                      help="Get all events")
    async def qev(self, ctx):
        arr = []
        query_dic = {
            "start_date": {"$lt": datetime.datetime.now()},
            "end_date": {"$gt": datetime.datetime.now()}
        }
        for row in self.db.find(query_dic):
            del row['_id']
            row['start_date'] = row['start_date'].strftime('%Y-%m-%d %H:%M:%S')
            row['end_date'] = row['end_date'].strftime('%Y-%m-%d %H:%M:%S')
            arr.append(row)
        res_df = pd.DataFrame(arr)
        if len(arr) != 0:  # TODO: STUPID HOTFIX
            res_df.columns = ["Event Name", "Event Description", "Start Date", "End Date"]
        await ctx.send("```\n" + res_df.to_string() + "\n```")

    @commands.command(name='addev', aliases=['addevent'],
                      help="Add event to be reminded daily")
    async def add_event(
            self,
            ctx,
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


master_bot.add_cog(DNSkillQuery(master_bot))
master_bot.add_cog(Venti(master_bot))
master_bot.add_cog(DNReminderEventBot(master_bot))
master_bot.add_cog(DNSTGReq(master_bot))

print("Bot started...")
master_bot.run(TOKEN)
