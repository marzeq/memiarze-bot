import discord
from discord.ext import commands
import main
import re


class WhoAskedBlocker(commands.Cog):
    def __init__(self, client: main.MemiarzeClient):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        splittingchars = " ,<.>/?;:'\"[{\\]}\\|\\-_=+`~!*()^&"
        match = re.match(f"[{splittingchars}]*(?:who|kto|czy)[{splittingchars}]*(?:asked|pytał(?:em|am)?)", message.content)

        if match:
            await message.delete()


def setup(client: main.MemiarzeClient):
    client.add_cog(WhoAskedBlocker(client))
