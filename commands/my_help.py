import discord

from discord.ext import commands

class MyHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        """
        This is triggered when !help is invoked.

        This example demonstrates how to list the commands that the member invoking the help command can run.
        """
        filtered = await self.filter_commands(self.context.bot.commands, sort=True) # returns a list of command objects
        names = [command.name for command in filtered] # iterating through the commands objects getting names
        available_commands = "" # joining the list of names by a new line)
        for command in filtered:
            command_str = f"!{command.name}"
            for parameter in command.clean_params.keys():
                print(parameter)
                command_str += f" [{parameter}]"
            available_commands += command_str + "\n"
          
        embed  = discord.Embed(description=available_commands, title="Commands")
        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        """This is triggered when !help <command> is invoked."""
        await self.context.send("This is the help page for a command")

    async def send_group_help(self, group):
        """This is triggered when !help <group> is invoked."""
        await self.context.send("This is the help page for a group command")

    async def send_cog_help(self, cog):
        """This is triggered when !help <cog> is invoked."""
        await self.context.send("This is the help page for a cog")

    async def send_error_message(self, error):
        """If there is an error, send a embed containing the error."""
        channel = self.get_destination() # this defaults to the command context channel
        await channel.send(error)
