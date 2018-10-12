import discord
import asyncio
from singletons.disc import Discord_bot
import embeds


disc = Discord_bot()
client = disc.get_client()

class Command:
    activation_string = ""
    help_string = ""

    async def action(self, bot, message):
        raise NotImplementedError

    # default help message for every command (!command help)
    async def help(self, message):
        await client.send_message(message.channel, embed=embeds.Info("Help for command `%s`" % self.activation_string, self.help_string))


class StopCommand(Command):
    activation_string = "!stop"
    help_string = "DEVELOPMENT ONLY - stops the bot"

    async def action(self, bot, message):
        await client.logout()