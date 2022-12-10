import difflib
import string
from datetime import datetime, timezone, timedelta
from typing import Literal, List

import pandas as pd
from discord import app_commands, Interaction
from discord.ext import commands
from src.db.db import DB


class DNDungeonKilos(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.df = pd.read_csv('dungeon.csv')
        self.prefix = '/'
        self.thresh = 0.6
        self.matcher = difflib.SequenceMatcher(lambda x: x == ' ')
        self.db = DB().get_client().dn_current_lucky_zone.dn_current_lucky_zone

    def sim_score(self, str_1: str, str_2: str) -> float:
        self.matcher.set_seqs(str_1.lower(), str_2.lower())
        return self.matcher.ratio()

    async def dg_autocomplete(self,
                              interaction: Interaction,
                              current: str,
                              ) -> List[app_commands.Choice[str]]:
        if len(current) < 5:
            choices = []
        else:
            choices = self.df["Name Called"].to_list()
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    @app_commands.command(name='dg',
                          description='Check what dungeons are Lucky Zone today')
    async def dg(self, i: Interaction) -> None:
        res = self.db.find_one({'id': 1})
        await i.response.send_message(f"""```Today's dungeon (valid until {res['date'].strftime('%Y-%m-%d %H:%M:%S')})
{self.df.iloc[[res['dg1'], res['dg2'],res['dg3']]][["Name in Selection", "Location", "Kilos Material"]].to_string()}```
""")

    @app_commands.command(name='dgup',
                          description='Update which dungeons are Lucky Zone')
    @app_commands.autocomplete(dg1=dg_autocomplete, dg2=dg_autocomplete, dg3=dg_autocomplete)
    async def dgup(self, i: Interaction, dg1: str, dg2: str, dg3: str, day: int, month: int, year: int) -> None:
        tmp = self.df[self.df["Name Called"].isin([dg1, dg2, dg3])].index.to_list()
        self.db.replace_one({'id': 1}, {
            'id': 1,
            'dg1': tmp[0],
            'dg2': tmp[1],
            'dg3': tmp[2],
            'date': datetime(year, month, day, 8, 59, 59, tzinfo=timezone(timedelta(hours=8)))
        }, upsert=True)
        await i.response.send_message(f"Lucky Zone Updated.")

    @app_commands.command(name='dgq',
                          description='Query dungeon name')
    async def dgq(self, i: Interaction, name: str) -> None:
        tmp = self.df.copy()
        tmp['Score'] = tmp["Name in Selection"].map(lambda x: self.sim_score(x, name))
        tmp.sort_values('Score', inplace=True, ascending=False)
        res = tmp[tmp['Score'] > self.thresh]
        await i.response.send_message("```\n" + res.to_string() + "```\n")

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.prefix == self.prefix
