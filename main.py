import discord
import os
import asyncio
import nest_asyncio
import json

from commands.my_help import MyHelp
from classes.database import Database
from dotenv import load_dotenv

load_dotenv()
nest_asyncio.apply()

from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.members = True
intents.reactions = True

help_command = commands.DefaultHelpCommand(no_category='Commands')

bot = commands.Bot(command_prefix="!",
                      intents=intents,
                      help_command=MyHelp())

async def load():
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      await bot.load_extension(f"cogs.{filename[:-3]}")

TOKEN = os.getenv("DISCORD_BOT_SECRET")

async def main():
  await load()
  await bot.run(TOKEN)

asyncio.run(main())




