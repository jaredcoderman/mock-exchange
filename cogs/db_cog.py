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
    if len(saved_stocks.keys()) != 20:
      saved_stocks = {
        "pear": 150,
        "macrosoft": 225,
        "boblox": 50,
        "alphabit": 175,
        "franklin": 85,
        "flutter": 10,
        "meta": 290,
        "ultra": 1000,
        "velcrox": 490,
        "penny": 1,
        "indigo": 750,
        "valve": 300,
        "plankton": 10000,
        "sahara": 600,
        "streamly": 80,
        "triangle": 180,
        "mash": 45,
        "tungsten": 275,
        "mango": 120,
        "surge": 850
      }
    stock_cog.stocks = {
      "pear": Stock("Pear", saved_stocks["pear"], 150),
      "macrosoft": Stock("Macrosoft", saved_stocks["macrosoft"], 225),
      "boblox": Stock("Boblox", saved_stocks["boblox"], 50),
      "alphabit": Stock("Alphabit", saved_stocks["alphabit"], 175),
      "franklin": Stock("Franklin", saved_stocks["franklin"], 85),
      "flutter": Stock("Flutter", saved_stocks["flutter"], 10),
      "meta": Stock("Meta", saved_stocks["meta"], 290),
      "ultra": Stock("Ultra", saved_stocks["ultra"], 1000),
      "velcrox": Stock("Velcrox", saved_stocks["velcrox"], 490),
      "penny": Stock("Penny", saved_stocks["penny"], 1),
      "indigo": Stock("Indigo", saved_stocks["indigo"], 750),
      "valve": Stock("Valve", saved_stocks["valve"], 300),
      "plankton": Stock("Plankton", saved_stocks["plankton"], 10000),
      "sahara": Stock("Sahara", saved_stocks["sahara"], 600),
      "streamly": Stock("Streamly", saved_stocks["streamly"], 80),
      "triangle": Stock("Triangle", saved_stocks["triangle"], 180),
      "mash": Stock("Mash", saved_stocks["mash"], 45),
      "tungsten": Stock("Tungsten", saved_stocks["tungsten"], 275),
      "mango": Stock("Mango", saved_stocks["mango"], 120), 
      "surge": Stock("Surge", saved_stocks["surge"], 850)
    }
    
    # Now that DBCog is setup, stocks can start running and update prices in db
    asyncio.run(stock_cog.callback())


async def setup(bot):
  await bot.add_cog(DBCog(bot))
