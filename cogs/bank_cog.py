from distutils import command
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


  # Check and set roles for net worth
  async def update_roles(self, user_id):
    
    # Dict that stores roles and their associated values
    networth_roles = {
      "Whale": 1000000,
      "Bronze Whale": 2500000,
      "Silver Whale": 5000000,
      "Gold Whale": 10000000,
      "Platinum Whale": 20000000,
      "Diamond Whale": 50000000,
      "Ruby Whale": 100000000,
      "Grandmaster": 250000000,
      "Billionaire": 1000000000,
      "Trillionaire": 1000000000000 
    }
    networth = self.get_net_worth(user_id)

    # Get the role the user should have
    new_role = ""
    for role, value in networth_roles.items():
      if networth >= value:
        new_role = role

    # Find guilds that have this bot that the user is in
    guilds = []
    members = []
    for guild in self.bot.guilds:
      member = await guild.fetch_member(user_id)
      if member:
        guilds.append(guild)
        members.append(member)

    # Remove roles they shouldn't have
    for member in members:
      for role in member.roles: 
        if role.name in networth_roles.keys() and role.name != new_role:
          await member.remove_roles(role)
    
    # Return if they dont have enough for any roles
    if new_role == "":
      return

    # Check if they have the role
    for guild in guilds:
      role_obj = None
      for role in guild.roles:
        if role.name == new_role:
          role_obj = role
          break
      for member in members:
        if member.get_role(role_obj.id):
          continue
        await member.add_roles(role_obj)
    

  # Get daily $1000
  @commands.command("daily")
  @commands.cooldown(1, 86400, commands.BucketType.user)
  async def daily(self, ctx):
    id = str(ctx.author.id)
    await self.bank.change_cash(id, 1000)
    msg = f"<@{id}> claimed their daily reward for $1000"
    await ctx.send(msg)

  @commands.command("setcash")
  @commands.has_any_role("Admin")
  async def setcash(self, ctx, user_at, amt):
    this_id = str(ctx.author.id)
    user_id = user_at[2:-1]
    amt = int(amt)
    await self.bank.set_cash(user_id, amt)
    msg = f"<@{this_id}> set {user_at}'s cash too {amt}"
    await ctx.send(msg)
      
  # Check total balance
  @commands.command("balance")
  async def balance(self, ctx, user_at=None):
    id = str(ctx.author.id)
    user_to_get = id
    display_name = str(ctx.author.name)
    if user_at != None:
      user_to_get = user_at[2:-1]
      user_obj = await self.bot.fetch_user(user_at[2:-1])
      display_name = user_obj.display_name
    amt = str(round(self.bank.get_cash(user_to_get), 2))
    msg = f"<@{id}>\n{display_name} has ${amt}"
    await ctx.send(msg)

  def get_net_worth(self, user_id):
    balance = self.bank.get_cash(user_id)
    portfolio_value = self.bot.get_cog("StockCog").get_share_value_dict_for_stock(user_id)["total_value"]
    return round(balance + portfolio_value, 2)

  # Get self or other net worth
  @commands.command("networth")
  async def networth(self, ctx, user_at=None):
    commander_id = str(ctx.author.id)
    display_name = ctx.author.name
    user_to_get = commander_id
    if user_at != None:
      user_to_get = user_at[2:-1]
      print(user_to_get)
      user_at_obj = await self.bot.fetch_user(user_to_get)
      display_name = user_at_obj.display_name
    balance = self.bank.get_cash(user_to_get)
    portfolio_value = self.bot.get_cog("StockCog").get_share_value_dict_for_stock(user_to_get)["total_value"]
    networth = round(balance + portfolio_value, 2)

    embed = discord.Embed(
      colour= discord.Colour.brand_green(),
      title= f"{display_name}'s Net Worth",
      description= f"Net Worth: ${networth}"
    )
    embed.add_field(name="Balance", value=f"${round(balance, 2)}")
    embed.add_field(name="Portfolio", value=f"${round(portfolio_value, 2)}")
    await ctx.send(embed=embed)

  @commands.command("donate")
  async def donate(self, ctx, user_at, amt):
    donor = str(ctx.author.id)
    donee = user_at[2:-1]
    amt = float(amt)
    # Check donor has amount they are donating
    if self.bank.get_cash(donor) < amt:
      await ctx.send(f"<@{donor}> You can't donate more money than you have!")
    
    # Remove amount from donor and add amount to donee
    await self.bank.change_cash(donor, amt * -1)
    await self.bank.change_cash(donee, amt)
    await ctx.send(f"<@{donor}> donated ${amt} to <@{donee}>")
      
    

async def setup(bot):
  await bot.add_cog(BankCog(bot))