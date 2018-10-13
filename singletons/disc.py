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

    async def send_message(self, channel, content="", embed=None):
        '''
            Just a wrapper for sending messages, so I don't have to deal with exceptions inside code
        '''
        try:
            await self.client.send_message(channel, content=content, embed=embed)
        except:
            print("ERROR: cmonBruh")