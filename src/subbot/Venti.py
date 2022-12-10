from discord.ext import commands


class Venti(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.prefix = 'ehe'

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.prefix == self.prefix

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if "ehe" in message.content.lower():
            await message.channel.send("EHE TE NANDAYO")

    # @commands.command(name='')
    # async def ehe(self, ctx, *args):
    #     if ctx.author == bot.user:
    #         return
    #     # if "ehe" in ctx.message:
    #     await ctx.send("EHE TE NANDAYO")
