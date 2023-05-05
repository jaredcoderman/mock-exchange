import discord 
import random
import asyncio

from discord.ext import commands

class MinigameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      print("Minigame cog online...")

    @commands.command("stockbattle")
    async def stockbattle(self, ctx, user_at, amt):
      this_user = str(ctx.author.id)
      other_user = user_at[2:-1]
      this_member = await self.bot.fetch_user(this_user)
      this_display_name = this_member.display_name

      msg = await ctx.send(f"<@{other_user}>, {this_display_name} is challenging you to a stock battle for ${amt}, do you accept?")
      await msg.add_reaction("👍")
      await msg.add_reaction("👎")
      # @ other user and wait to see if they accept, if not, tell this_user it failed
      reaction, user = await self.bot.wait_for(
        "reaction_add",
        check=lambda reaction, user: reaction.message.id == msg.id
        and int(this_user) == user.id
        and reaction.emoji == "👍" or reaction.emoji == "👎",
        timeout=60,
      )

      if str(reaction) != "👍":   
        await ctx.send(f"<@{this_user}> stock battle request denied :(")
        return

      # Pick a stock
      stocks = self.bot.get_cog("StockCog").stocks
      random_stock = random.choice(list(stocks.values()))

      # Ask if next stock will be higher or lower
      stock_msg = await ctx.send(f"<@{this_user}> <@{other_user}>\nStock Chosen: {random_stock.name} - ${random_stock.get_price(True)}\nWill the next stock be higher or lower?")
      await stock_msg.add_reaction("📈")
      await stock_msg.add_reaction("📉")
      await asyncio.sleep(5)
      cache_msg = discord.utils.get(self.bot.cached_messages, id=stock_msg.id)
      reaction_users = {}
      higher_users = [user async for user in cache_msg.reactions[0].users()]
      lower_users = [user async for user in cache_msg.reactions[1].users()]
      print(higher_users, lower_users)

      # Pick next stock

async def setup(bot):
  await bot.add_cog(MinigameCog(bot))