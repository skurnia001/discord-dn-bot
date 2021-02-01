# bot.py
import os
import string
import csv
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='/')

dic1 = dict()
dic2 = dict()
with open('skill.csv', 'r', newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for row in reader:
        dic1[row[1].lower()] = {"class": row[2], "jade": row[3], "equipment": row[0]}
        dic2[row[0].lower()] = {"class": row[2], "jade": row[3], "skill": row[1]}


@bot.command(name='jsq', aliases=['jadeskillquery', ], help='Finds a class whose skill match the skill name given.')
async def jsq(ctx, *args):
    skill = ' '.join(args)
    skill = skill.lower()
    if skill in dic1:
        response = "This is {}'s skill for {}, equipment name: {}".format(dic1[skill]['class'], dic1[skill]['jade'], dic1[skill]['equipment'])
    else:
        response = "No skill found :("

    await ctx.send(response)


@bot.command(name='esq', aliases=['eqskillquery', ], help='Finds a class whose skill is in the equipment name given.')
async def jsq(ctx, *args):
    equipment = ' '.join(args)
    equipment = equipment.lower()
    if equipment in dic2:
        response = "This is {}'s equipment for {}, skill name: {}".format(dic2[equipment]['class'], dic2[equipment]['jade'], dic2[equipment]['skill'])
    else:
        response = "No equipment found :("

    await ctx.send(response)


bot.run(TOKEN)
