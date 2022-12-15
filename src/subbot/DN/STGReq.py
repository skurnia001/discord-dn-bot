import pandas as pd
from discord.ext import commands


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
        if command_source == 'stgreq':
            command_source = 'STG'
        await ctx.send("```\n" + f"{command_source} requirements for {stg}:\n" + res + "```\n")

