import discord
import asyncio
from singletons.disc import Discord_bot
import embeds
import config as cfg
from database.db import Database
from database.models import Servers
import teamup

disc = Discord_bot()
client = disc.get_client()

db = Database()

async def has_owner_role(message):
        '''
            Helper function to check message.author for owner role
            Returns false if owner_role not found, also replies with error embed
            Keeping the error message here, since it will be the same for all commands
        '''
        # access database to pull out data about current server (based on message.server.id)
        with db.connect() as session:
                server_data = (
                    session.query(Servers)
                    .filter_by(discord_server_id=message.server.id)
                    .first()
                )
                session.expunge_all()
         
        if server_data is not None:
            # just turn server_data into dict
            sd = server_data.as_dict()

        if server_data is None:
            # No data about this server has been found
            await disc.send_message(message.channel, embed=embeds.Error("Error executing command", "This server is not setup."))
            return False
        elif sd["timezone"] is None or sd["owner_role"] is None:
            # timezone or owner role hasn't been set up
            await disc.send_message(message.channel, embed=embeds.Error("Error executing command", "Server timezone or owner_role are missing."))
            return False
        elif sd["owner_role"] not in [role.id for role in message.author.roles]:
            # Server has data, but sender of the message doesn't have owner role
            await disc.send_message(message.channel, embed=embeds.Error("Error executing command", "Insufficient permissions."))
            return False
        else:
            # everything is cool
            return True

class Command:
    activation_string = ""
    help_string = ""

    async def action(self, bot, message):
        raise NotImplementedError

    # default help message for every command (!command help)
    async def help(self, message):
        await disc.send_message(message.channel, embed=embeds.Info("Help for command `%s`" % self.activation_string, self.help_string))

class Setup(Command):
    activation_string = "!setup"
    help_string = "lipsum" # TODO

    async def action(self, bot, message):
        await bot.setup(message)

class AddScrim(Command):
    activation_string = "!scrimadd"
    help_string = "lipsum" # TODO

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.add_scrim(message)

class DeleteScrim(Command):
    activation_string = "!scrimdelete"
    help_string = "lipsum" # TODO

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.delete_scrim(message)
            
class EditScrim(Command):
    activation_string = "!scrimedit"
    help_string = "lipsum" # TODO

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.edit_scrim(message)

class UpdateSchedule(Command):
    '''
        Stops the bot from within, because CTRL+C sometimes takes too long
    '''
    activation_string = "!update"
    help_string = "Manually updates schedule"

    async def action(self, bot, message):
        await bot.update_schedule(message)

class TeamupSetup(Command):
    '''
        Sets up TeamUP calendar key for working with this platform via their API
    '''
    activation_string = "!teamup"
    help_string = "lipsum"

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.teamup_setup(message)
                

class StopCommand(Command):
    '''
        Stops the bot from within, because CTRL+C sometimes takes too long
    '''
    activation_string = "!stop"
    help_string = "DEVELOPMENT ONLY - stops the bot"

    async def action(self, bot, message):
        await client.logout()
