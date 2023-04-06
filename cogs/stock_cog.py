import discord
import time
import matplotlib.pyplot as plt
import asyncio

from threading import Thread
from discord.ext import commands
from classes.stock import Stock

stocks = {
  "pear": Stock("Pear", 164.54),
  "macrosoft": Stock("Macrosoft", 285.06),
  "boblox": Stock("Boblox", 44.83),
  "alphabit": Stock("Alphabit", 103.36),
  "franklin": Stock("Franklin", 192.42),
  "flutter": Stock("Flutter", 10.36)
}

async def run_stocks(bot):
  global stocks
  channel = bot.get_channel(1090713568913146066)
  #msg = await channel.send("Loading stocks...")
  for x in range(0, 250):
    for stock in stocks.values():
      stock.get_next_price()
  while True:
    for stock in stocks.values():
      stock.get_next_price()
    await asyncio.sleep(3)
    #stock_msg = ""
    #for stock in stocks.values():
    #  stock_msg += f"{stock.name}: {round(stock.get_price(), 2)}#\n"
    #await msg.edit(content=stock_msg)
    #await msg.pin()


def callback(bot):
  asyncio.run(run_stocks(bot))

def get_image(stock):
  image = discord.File("test.png")
  plt.plot(stock.get_previous_prices())
  plt.xlabel("Seconds")
  plt.ylabel("Price Changes")
  plt.savefig("test.png")
  plt.close()
  return image

class StockCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
        
  @commands.Cog.listener()
  async def on_ready(self):
    print("Stock cog online...")
    asyncio.run(callback(self.bot))
    

  @commands.command("price")
  async def price(self, ctx, name):
    id = str(ctx.author.id)
    global stocks
    stock = stocks[name.lower()]
    price = str(round(stock.get_price(), 2))
    msg = f"<@{id}> {stock.name} is valued at ${price} per share"
    image = get_image(stock)
    await ctx.send(msg, file=image)

  @commands.command("buy")
  async def buy(self, ctx, name, amount):
    global stocks
    stock = stocks[name]
    price = round(stock.get_price(), 2)
    total_price = round(stock.get_price() * float(amount), 2)
    id = str(ctx.author.id)
    bank = self.bot.get_cog("BankCog").bank
    if bank.get_cash(ctx.guild.id, id) >= total_price:
      bank.change_cash(ctx.guild.id, id, total_price * -1)
      bank.add_certificate(ctx.guild.id, id, name, int(amount), total_price)
      shares, value = bank.get_shares(ctx.guild.id, id, name)
      msg = f"<@{id}> purchased {amount} shares of {stock.name} for ${total_price} at ${price} per share. You now have {str(shares)} shares"
      await ctx.send(msg)
    else:
      await ctx.send(f"<@{id}> not enough money. Total price is ${total_price}, you have ${str(bank.get_cash(ctx.guild.id, id))}")

  @commands.command("shares")
  async def shares(self, ctx, name):
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(ctx.guild.id, id, name)
    global stocks
    msg = f"<@{id}> has {str(shares)} shares in {name} worth ${str(value)}"
    await ctx.send(msg)

  @commands.command("sell")
  async def sell(self, ctx, name):
    global stocks
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(ctx.guild.id, id, name)
    price = round(stocks[name].get_price(), 2)
    total_sell_price = price * int(shares)
    profit = round((total_sell_price - value), 2)
    msg = await ctx.send(f"<@{id}> are you sure you want to sell {shares} {stocks[name].name} for a profit of ${profit}")
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    reaction, user = await self.bot.wait_for(
      "reaction_add",
      check=lambda reaction, user: reaction.message.id == msg.id
      and int(id) == user.id
      and reaction.emoji == "👍" or reaction.emoji == "👎",
      timeout=None,
    )
    if str(reaction) == "👍":
      bank.remove_shares(ctx.guild.id, id, name)
      bank.change_cash(ctx.guild.id, id, total_sell_price)
      msg = f"<@{id}> sold {shares} shares of {stocks[name].name} for ${round(total_sell_price, 2)} and made ${profit} in profit!"
      await ctx.send(msg)
    elif str(reaction) == "👎":
      await ctx.send(f"<@{id}> sale cancelled...")

async def setup(bot):
  await bot.add_cog(StockCog(bot))
  

    