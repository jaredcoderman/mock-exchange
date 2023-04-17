import discord

from discord.ext import commands
from classes.bank import Bank

class BankCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Bank cog online...")
    self.bank = Bank(self.bot)

  @commands.command("daily")
  @commands.cooldown(1, 86400, commands.BucketType.user)
  async def daily(self, ctx):
    id = str(ctx.author.id)
    self.bank.change_cash(id, 1000)
    msg = f"<@{id}> claimed their daily reward for $1000"
    await ctx.send(msg)
      

  @commands.command("balance")
  async def balance(self, ctx):
    id = str(ctx.author.id)
    amt = str(round(self.bank.get_cash(id), 2))
    msg = f"<@{id}> has ${amt}"
    await ctx.send(msg)
    

async def setup(bot):
  await bot.add_cog(BankCog(bot))