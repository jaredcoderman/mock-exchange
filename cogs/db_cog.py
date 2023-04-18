import discord
import asyncio
from discord.ext import commands
from classes.database import Database

from classes.stock import Stock

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
      "pear": Stock("Pear", saved_stocks["pear"], 150),
      "macrosoft": Stock("Macrosoft", saved_stocks["macrosoft"], 225),
      "boblox": Stock("Boblox", saved_stocks["boblox"], 50),
      "alphabit": Stock("Alphabit", saved_stocks["alphabit"], 175),
      "franklin": Stock("Franklin", saved_stocks["franklin"], 85),
      "flutter": Stock("Flutter", saved_stocks["flutter"], 10)
    }
    
    # Now that DBCog is setup, stocks can start running and update prices in db
    asyncio.run(stock_cog.callback())


async def setup(bot):
  await bot.add_cog(DBCog(bot))
