# bot.py
import difflib
import os
import string
import csv
from dotenv import load_dotenv
from discord.ext import commands
import pandas as pd

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=('/',))


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
        await ctx.send(tmp[tmp['Score'] > self.thresh])

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
        if message.author == bot.user:
            return
        if "ehe" in message.content.lower():
            await message.channel.send("EHE TE NANDAYO")

    # @commands.command(name='')
    # async def ehe(self, ctx, *args):
    #     if ctx.author == bot.user:
    #         return
    #     # if "ehe" in ctx.message:
    #     await ctx.send("EHE TE NANDAYO")


bot.add_cog(DNSkillQuery(bot))
bot.add_cog(Venti(bot))

bot.run(TOKEN)
