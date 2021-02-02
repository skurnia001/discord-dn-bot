# bot.py
import os
import string
import csv
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=('/', 'ehe'))


class DNSkillQuery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dic1 = dict()
        self.dic2 = dict()
        self.prefix = '/'

        with open('skill.csv', 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                self.dic1[row[1].lower()] = {"class": row[2], "jade": row[3], "equipment": row[0]}
                self.dic2[row[0].lower()] = {"class": row[2], "jade": row[3], "skill": row[1]}

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    @commands.command(name='jsq', aliases=['jadeskillquery', ],
                      help='Finds a class whose skill match the skill name given.')
    async def jsq(self, ctx, *args):
        skill = ' '.join(args)
        skill = skill.lower()
        if skill in self.dic1:
            response = "This is {}'s skill for {}, equipment name: {}".format(self.dic1[skill]['class'],
                                                                              self.dic1[skill]['jade'],
                                                                              self.dic1[skill]['equipment'])
        else:
            response = "No skill found :("

        await ctx.send(response)

    @commands.command(name='esq', aliases=['eqskillquery', ],
                      help='Finds a class whose skill is in the equipment name given.')
    async def jsq(self, ctx, *args):
        equipment = ' '.join(args)
        equipment = equipment.lower()
        if equipment in self.dic2:
            response = "This is {}'s equipment for {}, skill name: {}".format(self.dic2[equipment]['class'],
                                                                              self.dic2[equipment]['jade'],
                                                                              self.dic2[equipment]['skill'])
        else:
            response = "No equipment found :("

        await ctx.send(response)


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
        await message.channel.send("EHE TE NANDAYO")


bot.add_cog(DNSkillQuery(bot))
bot.add_cog(Venti(bot))

bot.run(TOKEN)
