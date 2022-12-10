import difflib
import string
from typing import Literal

import pandas as pd
from discord.ext import commands


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
