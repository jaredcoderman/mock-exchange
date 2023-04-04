import discord

from replit import db
from discord.ext import commands
from classes.bank import Bank

class BankCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bank = Bank()

  @commands.Cog.listener()
  async def on_ready(self):
    print("Bank cog online...")
    guild = discord.utils.get(self.bot.guilds, name="BotTesting")
    for member in guild.members:
      id = str(member.id)
      db["user_stocks"][id] = {}
      db["user_certificates"][id] = []

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    id = str(ctx.author.id)
    await ctx.send(f"<@{id}> {error}")

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