import discord
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import asyncio
import json

from threading import Thread
from discord.ext import commands
from classes.stock import Stock

def get_image(stock):
  image = discord.File("test.png")
  fig, ax = plt.subplots()
  fig.set_facecolor("#000000")
  ax.tick_params(axis='x', colors='white')
  ax.tick_params(axis='y', colors='white')

  prices = stock.get_previous_prices()
  last_price = round(prices[-1], 2)

  prev_price = prices[0]
  line_color = 'black'

  # plot the prices as a line plot
  for i, price in enumerate(prices):
      if price > prev_price:
          # prices went up, so make the line green
          line_color = 'green'
      elif price < prev_price:
          # prices went down, so make the line red
          line_color = 'red'
      
      # plot the current price as a line segment
      if i > 0:
          plt.plot([i-1, i], [prev_price, price], color=line_color, linestyle=":")

      # update the previous price
      prev_price = price

  prices = np.array(prices)
  changes = prices[1:] - prices[:-1]

  # create a mask for positive and negative changes
  mask_up = changes >= 0
  mask_down = changes < 0

  # plot the last price with a different color and marker style
  if changes[-1] >= 0:
      plt.scatter(len(prices)-1, prices[-1], s=50, marker='^', c='g', label=f"Current Share Price: ${last_price}")
  else:
      plt.scatter(len(prices)-1, prices[-1], s=50, marker='v', c='r', label=f"Current Share Price: ${last_price}")
  padding = len(prices) * 0.1
  ax.set_xlim([0, len(prices) - 1 + padding])
  plt.xlabel('Time', fontdict={'family': 'Courier New', 'size': 12, 'weight': '500'}).set_color("#ffffff")
  plt.ylabel('Price', fontdict={'family': 'Courier New', 'size': 12, 'weight': '500'}).set_color("#ffffff")
  plt.title(stock.name, fontdict={'family': 'Courier New', 'size': 16, 'weight': '900'}, loc="left").set_color("#ffffff")

  # Add a prefix ($) to the y-axis labels
  def currency_fmt(x, pos):
      return '${:,.0f}'.format(x)

  formatter = ticker.FuncFormatter(currency_fmt)
  ax.yaxis.set_major_formatter(formatter)

  #font
  plt.rcParams['font.family'] = 'Courier New'
  plt.rcParams['font.weight'] = "bold"
  for tick in ax.get_xticklabels():
    tick.set_fontname("Courier New")
  for tick in ax.get_yticklabels():
    tick.set_fontname("Courier New")

  legend = plt.legend(facecolor="#000000", labelcolor="white", edgecolor="#000000")
  current_axis = plt.gca()
  current_axis.set_facecolor('#000000')
  plt.savefig("test.png")

  plt.close()
  return image

class StockCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.stocks = {}
        
  async def check_alerts(self):
    # Loop every user's alerts
    alert_cog = self.bot.get_cog("AlertCog")
    while True:
      # Loop through users and their alerts
      for user_id, alerts_arr in alert_cog.get_users_and_alerts().items():
        for alert in alerts_arr:
          user = await self.bot.fetch_user(user_id)
          # Check all target alerts
          if alert["alert_type"] == "target":
            goal_diff = float(alert["value"]) - float(alert["price_when_created"])
            current_diff = self.stocks[alert["stock"]].get_price(True) - float(alert["price_when_created"])

            # Check positive target alerts
            if goal_diff > 0 and current_diff >= goal_diff:
              alert_cog.remove_alert(user_id, alert["id"])
              await user.send(f"{alert['alert_type']} Alert: {alert['stock']} hit {alert['value']}")
  
            # Check negative target alerts
            elif goal_diff < 0 and current_diff <= goal_diff:
              alert_cog.remove_alert(user_id, alert["id"])
              await user.send(f"{alert['alert_type']} Alert: {alert['stock']} hit {alert['value']}")
          # Check all profit alerts
          else:
            pass
      await asyncio.sleep(.5)

  async def run_stocks(self):
    while True:
      for stock in self.stocks.values():
        stock.get_next_price()
      await asyncio.sleep(2)

  async def callback(self):
    stocks_task = asyncio.create_task(self.run_stocks())
    alerts_task = asyncio.create_task(self.check_alerts())
    await asyncio.gather(stocks_task, alerts_task)

  @commands.Cog.listener()
  async def on_ready(self):
    print("Stock cog online...")
    

  @commands.command("price")
  async def price(self, ctx, name):
    id = str(ctx.author.id)
    stock = self.stocks[name.lower()]
    price = str(stock.get_price(True))
    msg = f"<@{id}> {stock.name} is valued at ${price} per share"
    image = get_image(stock)
    await ctx.send(msg, file=image)

  @commands.command("buy")
  async def buy(self, ctx, name, amount):
    stock = self.stocks[name]
    price = stock.get_price(True)
    bank = self.bot.get_cog("BankCog").bank
    
    id = str(ctx.author.id)
    if amount == "all":
      amount = bank.get_cash(id) // price
    total_price = round(stock.get_price(False) * float(amount), 2)
    if bank.get_cash(id) >= total_price:
      bank.change_cash(id, total_price * -1)
      bank.add_certificate(id, name, int(amount), total_price)
      shares, value = bank.get_shares(id, name)
      msg = f"<@{id}> purchased {amount} shares of {stock.name} for ${total_price} at ${price} per share. You now have {str(shares)} shares"
      await ctx.send(msg)
    else:
      await ctx.send(f"<@{id}> not enough money. Total price is ${total_price}, you have ${str(bank.get_cash(id))}")

  @commands.command("shares")
  async def shares(self, ctx, name):
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(id, name) 
    msg = f"<@{id}> has {str(shares)} shares in {name} worth ${str(value)}"
    await ctx.send(msg)

  def get_stock_profit(self, id: str, stock):
    bank = self.bot.get_cog("BankCog").bank
    shares, value = bank.get_shares(id, stock)
    avg_value = shares / value
    return round(self.stock.get_price(False) - avg_value, 2)

  @commands.command("portfolio")
  async def portfolio(self, ctx):
    total_stocks = {}
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    total_value = 0
    total_profit = 0
    for stock in self.stocks.keys():
      shares, value = bank.get_shares(id, stock)
      if shares > 0:
        total_stocks[stock] = {"shares": shares, "value": value}
        total_value += value
    msg = f"<@{id}>'s portfolio:\n"
    for stock, data in total_stocks.items():
      original_price = data["value"] / data["shares"]
      total_original_value = original_price * data['shares']
      total_current_value = self.stocks[stock].get_price(False) * data['shares']
      profit = round(total_current_value - total_original_value, 2)
      total_profit += profit
      emoji = ""
      if profit > 0:
        emoji = ":green_circle:"
      else:
        emoji = ":red_circle:"
      msg += f"{data['shares']} {stock.capitalize()}: ${round(data['value'], 2)} Profit: ${profit} {emoji}\n"
    total_emoji = ""
    if total_profit > 0:
      total_emoji = ":green_circle:"
    else:
      total_emoji = ":red_circle:"
    msg += f"Total Worth: ${round(total_value, 2)} Total Profit: ${round(total_profit, 2)} {total_emoji}"
    await ctx.send(msg)

  @commands.command("sell")
  async def sell(self, ctx, name):
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(id, name)
    price = self.stocks[name].get_price(True)
    total_sell_price = price * int(shares)
    profit = round((total_sell_price - (value)), 2)
    msg = await ctx.send(f"<@{id}> are you sure you want to sell {shares} {self.stocks[name].name} for a profit of ${profit}")
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
      bank.remove_shares(id, name)
      bank.change_cash(id, total_sell_price)
      msg = f"<@{id}> sold {shares} shares of {self.stocks[name].name} for ${round(total_sell_price, 2)} and made ${profit} in profit!"
      await ctx.send(msg)
    elif str(reaction) == "👎":
      await ctx.send(f"<@{id}> sale cancelled...")

  @commands.command("stocks")
  async def stocks(self, ctx):
    msg = ""
    for stock in self.stocks.values():
      msg += f"{stock.name}: ${stock.get_price(True)}\n"
    await ctx.send(msg)

  @commands.has_any_role("Admin")
  @commands.command("savestocks")
  async def savestocks(self, ctx):
    saved_stocks = {}
    for stock_name, stock_obj in self.stocks.items():
      saved_stocks[stock_name] = stock_obj.get_price(False)
    db = self.bot.get_cog("DBCog").db
    data = db.get_record()
    data["stock_prices"] = saved_stocks
    db.update_data(json.dumps(data))
    await ctx.send("Saving stocks!")

  def is_stock(self, stock: str):
    if stock in self.stocks.keys():
      return True
    return False


async def setup(bot):
  await bot.add_cog(StockCog(bot))
  

    