import discord
from discord.ext import commands
import main
import utils
import orm.moderation


class Mutes(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.command(name="mute")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided!"):
        mutes_orm = orm.moderation.Mutes(self.client)

        mute = await mutes_orm.create(member, reason)

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Muted {mute.user.name}#{mute.user.discriminator} for: \"{reason}\""
        ))

    @commands.command(name="temp_mute", aliases=["tempmute"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def temp_mute(self, ctx: commands.Context, member: discord.Member, tme: str, *,
                        reason: str = "No reason provided!"):
        tempmutes_orm = orm.moderation.TempMutes(self.client)

        endtime = utils.process_time(tme)

        tempmute = await tempmutes_orm.create(member, reason, round(endtime))

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Tempmuted {tempmute.user.name}#{tempmute.user.discriminator} for: \"{reason}\""
        ))

    @commands.command(name="unmute", aliases=["un_mute"])
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        mutes_orm = orm.moderation.Mutes(self.client)

        mute = mutes_orm.get_mute_by_member(member)

        await mute.remove()

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Unmuted {mute.user.name}#{mute.user.discriminator}"
        ))


def setup(client: main.MemiarzeClient):
    client.add_cog(Mutes(client))
