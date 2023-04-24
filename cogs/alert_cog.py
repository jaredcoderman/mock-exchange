import discord
import uuid
import json

from discord.ext import commands

class AlertCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Alert cog ready...")

  # Get array of users and their alerts
  def get_users_and_alerts(self):
    db = self.bot.get_cog("DBCog").db
    record = db.get_record()
    return record["alerts"]

  # Get alerts for a specific user
  def get_alerts(self, id: str):
    db = self.bot.get_cog("DBCog").db
    record = db.get_record()
    if id in record["alerts"]:
      return record["alerts"][id]
    else:
      return []

  # Remove an alert given a user_id and alert id
  def remove_alert_from_db(self, user_id: str, uuid: str):
    db = self.bot.get_cog("DBCog").db
    record = db.get_record()
    for index, alert in enumerate(record["alerts"][user_id], start=0):
      if alert["id"] == uuid:
        print("Found")
        record["alerts"][user_id].pop(index)
        db.update_data(json.dumps(record))
        return

  @commands.command("alert")
  async def alert(self, ctx, stock_name, alert_type, value):
    # Check if they have max alerts
    str_id = str(ctx.author.id)
    alerts = self.get_alerts(str_id)
    if len(alerts) >= 3:
      await ctx.send(f"Error: <@{str_id}> You already have 3 alerts!")
      return

    # Check if stock exists
    stock_cog = self.bot.get_cog("StockCog")
    if not stock_cog.is_stock(stock_name):
      await ctx.send(f"Error: <@{str_id}> {stock_name} is not a stock! Use !stocks to see a list")
      return

    # Check if alert_type is target or profit
    if not alert_type in ("target", "profit"):
      await ctx.send(f"Error: <@{str_id}> {alert_type} is not a valid alert type, try 'target' or 'profit'")
      return

    # Create alert dict
    alert_dict = {
      "id": str(uuid.uuid4()),
      "stock": stock_name,
      "alert_type": alert_type
    }

    # Check if alert value for alert_type target is only numbers
    if alert_type == "target":
      if value.isnumeric(): 
        alert_dict["value"] = value
        alert_dict["price_when_created"] = stock_cog.stocks[stock_name].get_price(True)
      else:
        await ctx.send(f"Error: <@{str_id}> {value} is not a valid alert value, it must be only numbers when using 'target'")
        return

    # Check if alert value for alert_type profit is either only numbers or starts with percent
    if alert_type == "profit":
      if value.isnumeric():
        alert_dict["value"] = value
      elif value[:-1].isnumeric() and value[-1] == "%":
        alert_dict["value"] = value
      else:
        await ctx.send(f"Error: <@{str_id}> {value} is not a valid alert value, it must start with % or only contain numbers when using 'profit'")
        return
    
    # Write the new alert to the db
    db = self.bot.get_cog("DBCog").db
    record = db.get_record()
    if str_id in record["alerts"].keys():
      record["alerts"][str_id].append(alert_dict)
    else:
      record["alerts"][str_id] = [alert_dict]
    db.update_data(json.dumps(record))
    await ctx.send(f"<@{str_id}> alert added successfully! Type !alerts to view all your alerts")
    
  # Send a msg that displays user's alerts so they can remove them or remember
  @commands.command("alerts")
  async def alerts(self, ctx):
    str_id = str(ctx.author.id)
    alerts = self.get_alerts(str_id)
    msg = f"<@{str_id}>'s Alerts:\n"
    for index, alert in enumerate(alerts, start=1):
      if alert["alert_type"] == "target":
        msg += f"Alert {index}: {alert['stock'].capitalize()} hitting ${alert['value']}\n"
      else:
        msg += f"Alert {index}: {alert['stock'].capitalize()} hitting ${alert['value']} profit\n"
    await ctx.send(msg)

  # Command to remove an alert given a number which can be found from !alerts
  @commands.command("remove_alert")
  async def remove_alert(self, ctx, number):
    print(self, ctx, number)
    str_id = str(ctx.author.id)
    alerts = self.get_alerts(str_id)
    self.remove_alert_from_db(str_id, alerts[int(number)-1]["id"])
    await ctx.send(f"<@{str_id}> alert removed successfully!")

async def setup(bot):
  await bot.add_cog(AlertCog(bot))