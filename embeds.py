import discord
from datetime import datetime


def add_embed_footer(embed):
    embed.set_footer(
        text="Scrims scheduler bot by BlueX | " + datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
        icon_url="https://cdn.discordapp.com/avatars/162554458469957632/c84e8dc5798eb16113f915c4443b15ab.png",
    )


def Info(title, description):
    embed = discord.Embed(title=title, description=description, color=0x007BFF)
    add_embed_footer(embed)
    return embed


def Success(title, description):
    embed = discord.Embed(title=title, description=description, color=0x28A745)
    add_embed_footer(embed)
    return embed


def Error(title, description):
    embed = discord.Embed(title=title, description=description, color=0xDC3545)
    add_embed_footer(embed)
    return embed

