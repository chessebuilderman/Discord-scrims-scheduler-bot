import discord
from singletons.disc import Discord_bot
import random
from database.models import Servers

disc = Discord_bot()
client = disc.get_client()


class Scrim_bot:
    version = "DEV"
    commands = []