# bot.py
import os
import string
import csv
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='/')

dic = dict()
with open('skill.csv', 'r', newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for row in reader:
        dic[row[0]] = {"class": row[1], "jade": row[2]}


@bot.command(name='jsq', aliases=['jadeskillquery', ], help='Finds a class whose skill match the skill name given '
                                                            'if they have that skill as the skill of some dragon jade.')
async def jsq(ctx, *args):
    skill = ' '.join(args)
    skill = string.capwords(skill)
    if skill in dic:
        response = "This is {}'s skill for {}".format(dic[skill]['class'], dic[skill]['jade'])
    else:
        response = "No jade found using this skill :("

    await ctx.send(response)


bot.run(TOKEN)
