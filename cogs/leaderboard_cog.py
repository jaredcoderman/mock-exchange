import discord

from discord.ext import commands

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Leaderboard cog online...")

        # Shows top 10 players net worths and the user who called it's place in total players
    @commands.command("leaderboard")
    async def leaderboard(self, ctx):
        # 1. Get all players and their net worth
        db = self.bot.get_cog("DBCog").db
        data = db.get_record()
        members = data["user_money"].keys()
        net_worths = {}
        for member in members:
            net_worths[member] = self.bot.get_cog("BankCog").get_net_worth(member)

        # 2. Sort those players highest to lowest
        sorted_members = sorted(net_worths.items(), key=lambda x: x[1], reverse=True)

        # 3. Store the user who called the commands place
        this_user = str(ctx.author.id)
        this_users_place = 0
        for index, pair in enumerate(sorted_members):
            if pair[0] == this_user:
                this_users_place = index + 1
                break

        # 4. Trim the list to 10 players if there are more than 10
        if len(sorted_members) > 10:
            sorted_members = sorted_members[:10]

        # 5. Loop through the list and add each player to a string
        embed = discord.Embed(
        colour= discord.Colour.brand_green(),
        title= "Net Worth Leaderboard",
        )
        msg = ""
        for index,pair in enumerate(sorted_members):
            member_obj = await self.bot.fetch_user(pair[0])
            msg += f"**{index+1}** - {member_obj.display_name}: ${pair[1]}\n"

        # 6. @ the user and print the string
        msg += f"<@{this_user}>'s Place: {this_users_place}"
        embed.description = msg
        await ctx.send(embed=embed)

async def setup(bot):
  await bot.add_cog(LeaderboardCog(bot))