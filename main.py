import discord
import asyncio
import bot
import commands
from singletons.disc import Discord_bot
from database.db import Database
import config as cfg

disc = Discord_bot()
client = disc.get_client()

bot = bot.Scrim_bot()

bot.commands.append(commands.StopCommand())

db = Database()

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


@client.event
async def on_message(message):
    for command in bot.commands:
        if message.content.startswith(command.activation_string):
            vals = message.content.split(" ")
            if(len(vals) > 1):
                if vals[1] == "help":
                    await command.help(message)
                    return

            await command.action(bot, message)
            return

client.run( cfg.bot["prod_token"] if cfg.bot["version"] == "prod" else cfg.bot["dev_token"])