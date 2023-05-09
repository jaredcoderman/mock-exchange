import discord

from discord import Color as c
from discord.ext import commands

class ServerCog(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
  
  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    print(f"Joined guild! {guild.name}")
    await guild.create_role(name="Trillionaire", color=c.from_str("#E74C3C"))
    await guild.create_role(name="Billionaire", color=c.from_str("#AD1457"))
    await guild.create_role(name="Grandmaster", color=c.from_str("#2ECC71"))
    await guild.create_role(name="Ruby Whale", color=c.from_str("#DB0000"))
    await guild.create_role(name="Diamond Whale", color=c.from_str("#3498DB"))
    await guild.create_role(name="Platinum Whale", color=c.from_str("#206694"))
    await guild.create_role(name="Gold Whale", color=c.from_str("#F1C40F"))
    await guild.create_role(name="Silver Whale", color=c.from_str("#95A5A6"))
    await guild.create_role(name="Bronze Whale", color=c.from_str("#C27C0E"))
    await guild.create_role(name="Whale", color=c.from_str("#99AAB5"))
    await guild.create_role(name="StockAdmin", color=c.from_str("#992D22"))


async def setup(bot):
  await bot.add_cog(ServerCog(bot))