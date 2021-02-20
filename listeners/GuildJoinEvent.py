import discord
from discord.ext import commands
import main


class Mutes(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.client.cursor.execute("insert into guilds (id) values (:id)", {"id", guild.id})
        self.client.conn.commit()


def setup(client: main.MemiarzeClient):
    client.add_cog(Mutes(client))
