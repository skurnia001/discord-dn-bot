import datetime
from typing import Literal

import pandas as pd
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import relativedelta
from discord.ext import commands

from src.db.db import DB


class DNReminderEventBot(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.reminder_callback, CronTrigger(hour="0, 18, 21, 23"))
        self.scheduler.start()
        self.channel_id = channel_id
        self.db = DB().get_client().dn_event_db.dn_event_db

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
        c = self.bot.get_channel(self.channel_id)
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
