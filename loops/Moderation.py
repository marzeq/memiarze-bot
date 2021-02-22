from discord.ext import commands, tasks
import main
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

        tempbans_orm: orm.moderation.TempBans = orm.moderation.TempBans(self.client)

        tempbans = await tempbans_orm.get_bans_before(time.time())
        for tempban in tempbans:
            await tempban.remove()


def setup(client: main.MemiarzeClient):
    obj = Moderation(client)
    obj.check_punishments.start()
    client.add_cog(obj)
