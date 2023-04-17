import discord
import json
import asyncio
from discord.ext import commands
from pathlib import Path
from classes.database import Database

from classes.stock import Stock

def get_init_db_data(guilds):
  default_dict = {
    "user_money": {},
    "user_certificates": {}
  }
  for guild in guilds:
    for member in guild.members:
      default_dict["user_money"][str(member.id)] = 0
      default_dict["user_certificates"][str(member.id)] = []
  return json.dumps(default_dict)

class DBCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.guilds = []
    self.db = Database()

  @commands.Cog.listener()
  async def on_ready(self):
    print("Database cog online...")
    self.db.init_data()
    saved_stocks = self.db.get_saved_stock_prices()
    stock_cog = self.bot.get_cog("StockCog")
    if len(saved_stocks.keys()) == 0:
      saved_stocks = {
        "pear": 150,
        "macrosoft": 225,
        "boblox": 50,
        "alphabit": 175,
        "franklin": 85,
        "flutter": 10
      }
    stock_cog.stocks = {
      "pear": Stock("Pear", saved_stocks["pear"]),
      "macrosoft": Stock("Macrosoft", saved_stocks["macrosoft"]),
      "boblox": Stock("Boblox", saved_stocks["boblox"] ),
      "alphabit": Stock("Alphabit", saved_stocks["alphabit"]),
      "franklin": Stock("Franklin", saved_stocks["franklin"]),
      "flutter": Stock("Flutter", saved_stocks["flutter"])
    }
    asyncio.run(stock_cog.callback())
    #data = get_init_db_data(self.bot.guilds)
    #self.db.update_data(data)


async def setup(bot):
  await bot.add_cog(DBCog(bot))
