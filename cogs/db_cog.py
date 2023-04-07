import discord
import json

from discord.ext import commands
from pathlib import Path

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

  @commands.Cog.listener()
  async def on_ready(self):
    file = Path(f"./data/db.json")
    if not file.is_file():
      with open(f"./data/db.json", "w") as f:
        data = get_init_db_data(self.bot.guilds)
        f.write(data)

async def setup(bot):
  await bot.add_cog(DBCog(bot))
