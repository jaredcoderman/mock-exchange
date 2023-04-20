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

  # Get daily $1000
  @commands.command("daily")
  @commands.cooldown(1, 86400, commands.BucketType.user)
  async def daily(self, ctx):
    id = str(ctx.author.id)
    self.bank.change_cash(id, 1000)
    msg = f"<@{id}> claimed their daily reward for $1000"
    await ctx.send(msg)
      
  # Check total balance
  @commands.command("balance")
  async def balance(self, ctx, user_id=None):
    id = str(ctx.author.id)
    user_to_get = id
    display_name = str(ctx.author.name)
    if user_id != None:
      user_to_get = user_id[2:-1]
      user_obj = await self.bot.fetch_user(user_id[2:-1])
      display_name = user_obj.display_name
    amt = str(round(self.bank.get_cash(user_to_get), 2))
    msg = f"<@{id}>\n{display_name} has ${amt}"
    await ctx.send(msg)
    

async def setup(bot):
  await bot.add_cog(BankCog(bot))