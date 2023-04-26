import discord
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

  # Set Fonts
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
  
  # Constantly checks stock prices and alerts to notify users
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
              alert_cog.remove_alert_from_db(user_id, alert["id"])
              await user.send(f"{alert['alert_type'].capitalize()} Alert: {alert['stock']} hit {alert['value']}")
  
            # Check negative target alerts
            elif goal_diff < 0 and current_diff <= goal_diff:
              alert_cog.remove_alert_from_db(user_id, alert["id"])
              await user.send(f"{alert['alert_type'].capitalize()} Alert: {alert['stock']} hit {alert['value']}")
          # Check all profit alerts
          else:
            bank = self.bot.get_cog("BankCog").bank
            shares, value = bank.get_shares(user_id, alert["stock"])
            current_price = self.stocks[alert["stock"]].get_price(False)
            profit = (current_price * shares) - value
            
            # Check if profit percent reached
            if alert["value"][-1] == "%":
              if (profit / value) * 100 > int(alert["value"][:-1]):
                alert_cog.remove_alert_from_db(user_id, alert["id"])
                await user.send(f"{alert['alert_type'].capitalize()} Alert: Your Profit for {alert['stock']} hit {alert['value']}")
            # Check if raw profit reached
            elif profit >= int(alert["value"]):
              alert_cog.remove_alert_from_db(user_id, alert["id"])
              await user.send(f"{alert['alert_type'].capitalize()} Alert: Your Profit for {alert['stock']} hit {alert['value']}")
      await asyncio.sleep(1)

  # Starts the stock price changges

  def get_above_initial_price_emoji(self, stock):
    if stock.get_price(False) > stock.initial_price:
      return ":green_circle:"
    return ":red_circle:"
    
  def get_trending_emoji(self, stock):
    if len(stock.get_previous_prices()) < 76:
      return ""
    if stock.get_previous_prices()[75] < stock.get_previous_prices()[-1]:
      return ":chart_with_upwards_trend:"
    return ":chart_with_downwards_trend:"


  async def run_stocks(self):
    count = 0
    general_channels = []
    pins_to_update = []

    # Get all general channels
    for guild in self.bot.guilds:
      for channel in guild.text_channels:
        if channel.name == "general":
          general_channels.append(channel)

    # Get pinned channels and created pins to update
    for channel in general_channels:
        pins = await channel.pins()
        if len(pins) > 0:
          pins_to_update.append(pins[0])
        else:
          msg="**Stock Prices**\n"
          for stock_name, stock in self.stocks.items():
            emoji = self.get_above_initial_price_emoji(stock)
            print(emoji)
            msg += f"{stock_name}: ${stock.get_price(True)} {emoji}\n"
          message = await channel.send(msg)
          await message.pin()
          pins_to_update.append(message)

    pin_count = 0
    while True:
      # Update stock prices
      for stock in self.stocks.values():
        stock.get_next_price()

      # Update pins
      if pin_count == 2:
        pin_count = 0
        for pin in pins_to_update:
          msg="**Stock Prices**\n"
          for stock_name, stock in self.stocks.items():
            msg += f"{stock_name}: ${stock.get_price(True)} {self.get_above_initial_price_emoji(stock)} {self.get_trending_emoji(stock)}\n"
          await pin.edit(content=msg)
      else:
        pin_count += 1

      count += 1
      if count == 100:
        count = 0
        await self.save_stocks()
      await asyncio.sleep(2)

  # Runs asynchronous functions
  async def callback(self):
    stocks_task = asyncio.create_task(self.run_stocks())
    alerts_task = asyncio.create_task(self.check_alerts())
    await asyncio.gather(stocks_task, alerts_task)

  @commands.Cog.listener()
  async def on_ready(self):
    print("Stock cog online...")
    
  # Checks the price of a stock
  @commands.command("price")
  async def price(self, ctx, stock_name):
    id = str(ctx.author.id)
    stock = self.stocks[stock_name.lower()]
    price = str(stock.get_price(True))
    msg = f"<@{id}> {stock.name} is valued at ${price} per share"
    image = get_image(stock)
    await ctx.send(msg, file=image)

  # Purchase a stock with a number of shares
  @commands.command("buy")
  async def buy(self, ctx, stock_name, amount):
    stock = self.stocks[stock_name]
    price = stock.get_price(False)
    bank = self.bot.get_cog("BankCog").bank
    
    id = str(ctx.author.id)
    if amount == "all":
      amount = bank.get_cash(id) // price
    elif amount[-1] == "%":
      amount = (int(amount[:-1]) / 100 * bank.get_cash(id)) // price
    total_price = round(stock.get_price(False) * float(amount), 2)


    if bank.get_cash(id) >= total_price:
      bank.change_cash(id, total_price * -1)
      bank.add_certificate(id, stock_name, int(amount), total_price)
      shares, value = bank.get_shares(id, stock_name)
      msg = f"<@{id}> purchased {amount} shares of {stock.name} for ${total_price} at ${price} per share. You now have {str(shares)} shares"
      await ctx.send(msg)
    else:
      await ctx.send(f"<@{id}> not enough money. Total price is ${total_price}, you have ${str(bank.get_cash(id))}")

  # Check your shares with a given stock
  @commands.command("shares")
  async def shares(self, ctx, stock_name):
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(id, stock_name) 
    msg = f"<@{id}> has {str(shares)} shares in {stock_name} worth ${str(value)}"
    await ctx.send(msg)

  def get_share_value_dict_for_stock(self, user_id: str):
    total_stocks = {}
    bank = self.bot.get_cog("BankCog").bank
    total_value = 0
    for stock in self.stocks.keys():
      shares, value = bank.get_shares(user_id, stock)
      if shares > 0:
        total_stocks[stock] = {"shares": shares, "value": value}
        total_value += value
    total_stocks["total_value"] = total_value
    return total_stocks

  # Check your stock portfolio
  @commands.command("portfolio")
  async def portfolio(self, ctx, user_at=None):
    # Setup necessary variables
    display_name = str(ctx.author.name)
    id = str(ctx.author.id)
    user_obj = await self.bot.fetch_user(str(ctx.author.id))
    if user_at != None:
      id = user_at[2:-1]
      user_obj = await self.bot.fetch_user(id)
      display_name = user_obj.display_name
    total_stocks = self.get_share_value_dict_for_stock(id)
    total_profit = 0

    # Create the message to send to the user
    embed = discord.Embed(
      colour= discord.Colour.brand_green(),
      title= f"{display_name}'s portfolio",
    )
    # For each stock, depending on its profitability, label it with a green circle or red circle 
    for stock, data in total_stocks.items():
      if stock == "total_value":
        continue
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
      embed.add_field(name=f"{data['shares']} {stock.capitalize()}", value=f"${round(data['value'], 2)} Profit: ${profit} {emoji}")
    total_emoji = ""
    if total_profit > 0:
      total_emoji = ":green_circle:"
    else:
      total_emoji = ":red_circle:"
    msg = f"Value: ${round(total_stocks['total_value'], 2)} | Profit: ${round(total_profit, 2)} {total_emoji}"
    # embed = discord.Embed(
    #   colour= discord.Colour.brand_green(),
    #   title= f"{display_name}'s portfolio",
    #   description={msg}
    # )

    embed.description = msg
    embed.set_thumbnail(url=user_obj.display_avatar)
    await ctx.send(embed=embed)

  # Sell a stock
  @commands.command("sell")
  async def sell(self, ctx, stock_name):
    # Get data for the message and functionality
    bank = self.bot.get_cog("BankCog").bank
    id = str(ctx.author.id)
    shares, value = bank.get_shares(id, stock_name)
    price = self.stocks[stock_name].get_price(True)
    total_sell_price = price * int(shares)
    profit = round((total_sell_price - (value)), 2)

    # Prompt the user
    msg = await ctx.send(f"<@{id}> are you sure you want to sell {shares} {self.stocks[stock_name].name} for a profit of ${profit}")
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

    # Wait for user reaction to confirm or deny sale
    reaction, user = await self.bot.wait_for(
      "reaction_add",
      check=lambda reaction, user: reaction.message.id == msg.id
      and int(id) == user.id
      and reaction.emoji == "👍" or reaction.emoji == "👎",
      timeout=None,
    )

    # Make the sale happen or cancel depending on reaction
    if str(reaction) == "👍":
      bank.remove_shares(id, stock_name)
      bank.change_cash(id, total_sell_price)
      msg = f"<@{id}> sold {shares} shares of {self.stocks[stock_name].name} for ${round(total_sell_price, 2)} and made ${profit} in profit!"
      await ctx.send(msg)
    elif str(reaction) == "👎":
      await ctx.send(f"<@{id}> sale cancelled...")

  # Get a list of stocks and their prices, along with their initial price
  @commands.command("stocks")
  async def stocks(self, ctx):
    msg = ""
    for stock in self.stocks.values():
      msg += f"{stock.name}: ${stock.get_price(True)}, Initial Price: ${stock.initial_price}\n"
    await ctx.send(msg)

  async def save_stocks(self):
    saved_stocks = {}
    for stock_name, stock_obj in self.stocks.items():
      saved_stocks[stock_name] = stock_obj.get_price(False)
    db = self.bot.get_cog("DBCog").db
    data = db.get_record()
    data["stock_prices"] = saved_stocks
    db.update_data(json.dumps(data))
    print("Saving stocks...")

  # Save stocks so that stock prices are the same after deployment
  @commands.has_any_role("Admin")
  @commands.command("savestocks")
  async def savestocks(self, ctx):
    await self.save_stocks()
    await ctx.send("Saving stocks!")

  # Check if a string is a stock
  def is_stock(self, stock: str):
    if stock in self.stocks.keys():
      return True
    return False


async def setup(bot):
  await bot.add_cog(StockCog(bot))
  

    