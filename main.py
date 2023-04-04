import discord
import os
import asyncio
import nest_asyncio
import db_init

nest_asyncio.apply()

from discord.ext import commands
from webserver import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.members = True

help_command = commands.DefaultHelpCommand(no_category='Commands')

bot = commands.Bot(command_prefix="!",
                      intents=intents,
                      help_command=help_command)

async def load():
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
  await load()
  await bot.run(os.environ['DISCORD_BOT_SECRET'])

asyncio.run(main())
keep_alive()




