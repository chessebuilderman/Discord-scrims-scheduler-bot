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
    example = ""

    async def action(self, bot, message):
        raise NotImplementedError

    # default help message for every command (!command help)
    async def help(self, message):
        help_embed = embeds.Info("Help for command `%s`" % self.activation_string, self.help_string)
        help_embed.add_field(name="Example", value=self.example)
        await disc.send_message(message.channel, embed=help_embed)

class Setup(Command):
    activation_string = "!setup"
    help_string = "Sets up the server for bot to use:\n**Arguments**:\n`!setup [timezone] [owner-role] [mention-role] [schedule-channel] [reminders-channel]`\nMake sure that roles are **MENTIONABLE**" # TODO
    example = "`!setup Europe/Bratislava @manager @member #schedule #reminder`"

    async def action(self, bot, message):
        await bot.setup(message)

class AddScrim(Command):
    activation_string = "!scrimadd"
    help_string = "Adds scrim to schedule:\n**Arguments**:\n`!scrimadd [date] [time-start] [time-end] [enemy-team-name]`" # TODO
    example = "`!scrimadd 17/10 18:00 20:00 Dallas Fuel`"

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.add_scrim(message)

class DeleteScrim(Command):
    activation_string = "!scrimdelete"
    help_string = "Deletes scrim by given ID:\n**Arguments**:\n`!scrimdelete [ID]`" # TODO
    example = "`!scrimdelete 1`"

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.delete_scrim(message)
            
class EditScrim(Command):
    activation_string = "!scrimedit"
    help_string = "Edits already existing scrim by its ID:\n**Arguments**:\n`!scrimedit [ID] [date] [time-start] [time-end] [enemy-team-name]`" # TODO
    example = "!scrimedit 1 18/10 20:00 22:00 Dallas Fuel"

    async def action(self, bot, message):
        if await has_owner_role(message):
            await bot.edit_scrim(message)

class UpdateSchedule(Command):
    '''
        Stops the bot from within, because CTRL+C sometimes takes too long
    '''
    activation_string = "!update"
    help_string = "Manually updates static schedule"

    async def action(self, bot, message):
        await bot.update_schedule(message)

class TeamupSetup(Command):
    '''
        Sets up TeamUP calendar key for working with this platform via their API
    '''
    activation_string = "!teamup"
    help_string = "Connects the bot to your TeamUP calendar:\n**Arguments**:\n`!teamup [calendar-key with admin permissions]`\n to disconnect use command `!teamup -`"
    example = "`!teamup ks73ad7816e7a61b3a`"

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
