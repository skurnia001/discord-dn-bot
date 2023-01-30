import pandas as pd
from discord.ext import commands

from src.utils.logger import setup_logger


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
        self.stgreq_command_ordered = ['crit', 'cdm', 'def', 'fd']
        self.stgreq_command_long = {
            'cdmg': 'Crit. Damage',
            'cdm': 'Crit. Damage',
            'crit': 'Critical',
            'def': 'Pdef/Mdef',
            'mdef': 'Pdef/Mdef',
            'fd': 'Final Damage',
        }
        self.logger = setup_logger("DNSTGReq")

    @commands.hybrid_command(name='stgreq', aliases=['crit', 'cdmg', 'cdm', 'def', 'mdef', 'fd'],
                             help='Returns the required stats given the stg requirement (13-25). ' +
                                  'Refer to the command alias for stats.')
    async def stgreq(self, ctx: commands.Context, stg: int) -> None:
        # Return error message if stg is not within range
        if stg not in range(self.stg_min, self.stg_max + 1):
            message = f"STG argument is wrong! Please enter a valid integer between {self.stg_min} and {self.stg_max}."
            await ctx.send(message)
            return

        # Get set of stats to
        stats = list()
        if ctx.invoked_with.lower() == "stgreq":
            stats.extend(self.stgreq_command_ordered)
        else:
            stats.append(ctx.invoked_with)

        # Generate and fill the output table
        res = []
        print(stats)

        for idx, stat in enumerate(stats):
            columns = self.command_mapper.get(stat, self.df.columns)
            print(f"columns to process are {columns}")
            # Return the stat for a given stg
            data = self.df[columns]
            data = data.loc[stg]
            print(data)
            entry = {
                "Index": idx,
                "Stat": self.stgreq_command_long[stat].title(),
                "Cap": data[0],
                "Penalty": data[1],
                "% Cap": data[2]
            }
            res.append(entry)

        # Let's make it pretty automatically using pandas!
        res_pd = pd.DataFrame(res)
        res_pd = res_pd.set_index('Index')

        message = f"__**Labyrinth {stg} Stat Cap**__"

        message += f"```CSS\n{res_pd.to_string(index=False)}```"

        await ctx.send(message)
