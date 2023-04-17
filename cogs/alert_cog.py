import discord

from discord.ext import commands

class AlertCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Alert cog ready...")

async def setup(bot):
  await bot.add_cog(AlertCog(bot))