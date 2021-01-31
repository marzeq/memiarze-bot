import discord
from discord.ext import commands, tasks
import main
import utils
import orm.moderation
import time


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @tasks.loop(seconds=1)
    async def check_punishments(self):
        tempmutes_orm: orm.moderation.TempMutes = orm.moderation.TempMutes(self.client)

        tempmutes = tempmutes_orm.get_mutes_before(time.time())
        for tempmute in tempmutes:
            await tempmute.remove()


def setup(client: main.MemiarzeClient):
    obj = Moderation(client)
    obj.check_punishments.start()
    client.add_cog(obj)
