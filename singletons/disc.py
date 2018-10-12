import discord
import asyncio


class Discord_bot:
    _instance = None
    client = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        if self.client is None:
            self.client = discord.Client()

            if self.client is not None:
                print("Discord bot pooling created successfully")

    def get_client(self):
        return self.client
