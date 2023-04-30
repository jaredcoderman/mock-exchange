import discord 

from discord.ext import commands

class MinigameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      print("Minigame cog online...")

    @commands.command("stockbattle")
    async def stockbattle(self, ctx, user_at):
      this_user = str(ctx.author.id)
      other_user = user_at[2:-1]
      this_member = await self.bot.fetch_user(this_user)
      this_display_name = this_member.display_name

      msg = await ctx.send(f"<@{other_user}, {this_display_name} is challenging you to a stock battle, do you accept?")
      await msg.add_reaction("👍")
      await msg.add_reaction("👎")
      # @ other user and wait to see if they accept, if not, tell this_user it failed
      reaction, user = await self.bot.wait_for(
        "reaction_add",
        check=lambda reaction, user: reaction.message.id == msg.id
        and int(id) == user.id
        and reaction.emoji == "👍" or reaction.emoji == "👎",
        timeout=60,
      )

      if str(reaction) != "👍":   
        await ctx.send(f"<@{this_user}> battle request denied :(")
      else:
        pass

async def setup(bot):
  await bot.add_cog(MinigameCog(bot))