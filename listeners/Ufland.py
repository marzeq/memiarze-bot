import discord
from discord.ext import commands
import requests
import json

"""
THIS IS LEGACY CODE AND IS BEING REWRITTEN
"""

with open("config.json") as f:
    config = json.load(f)["ufland"]


class Ufland(commands.Cog):
    gain = config["gain"]
    jsongain = {"bank": gain}
    jsonloose = {"bank": -gain}
    memes = config["memes"]
    logging = config["logging"]
    auth = config["auth"]

    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):

        if not (reaction.message.attachments or ("https://" in reaction.message.content)) or \
                user.bot or reaction.message.author.bot or str(reaction.emoji) != "🍞":
            return

        if reaction.message.channel.id == self.memes:
            if reaction.message.author != user:
                requests.patch(f"https://unbelievable.pizza/api/guilds/620296464337338410/users/"
                               f"{reaction.message.author.id}/",
                               json=self.jsongain, headers=self.auth)
                await self.client.fetch_channel(self.logging).send(f"Dodaje {self.gain}😂💯 do banku "
                                                                   f"{reaction.message.author.name}...")

            else:
                await reaction.remove(user)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        if not (reaction.message.attachments or ("https://" in reaction.message.content)) or \
                user.bot or reaction.message.author.bot or str(reaction.emoji) != "🍞":
            return

        if reaction.message.channel.id == self.memes \
                and reaction.message.author != user:
            requests.patch(f"https://unbelievable.pizza/api/guilds/620296464337338410/users/"
                           f"{reaction.message.author.id}/",
                           json=self.jsonloose, headers=self.auth)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not (message.attachments or ("https://" in message.content)) or message.author.bot:
            return
        if message.channel.id == self.memes:
            await message.add_reaction("🍞")


def setup(client: commands.Bot):
    obj = Ufland(client)
    if obj.memes != 0 and obj.logging != 0:
        client.add_cog(obj)
