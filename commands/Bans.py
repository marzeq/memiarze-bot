import discord
from discord.ext import commands
import main
import utils
import orm.moderation


class Bans(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.command(name="ban")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Nie podano powodu!"):
        bans_orm = orm.moderation.Bans(self.client)

        ban = await bans_orm.create(member, reason)

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Zbanowano {ban.user.name}#{ban.user.discriminator} za: \"{reason}\""
        ))

    @commands.command(name="temp_ban", aliases=["tempban"])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def temp_ban(self, ctx: commands.Context, member: discord.Member, tme: str, *,
                       reason: str = "Nie podano powodu!"):
        tempbans_orm = orm.moderation.TempBans(self.client)

        endtime = utils.process_time(tme)

        tempban = await tempbans_orm.create(member, reason, round(endtime))

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Czasowo zbanowano {tempban.user.name}#{tempban.user.discriminator} za: \"{reason}\""
        ))

    @commands.command(name="unban", aliases=["un_ban"])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User):
        bans_orm = orm.moderation.Bans(self.client)

        ban = await bans_orm.get_ban_by_member(user, ctx.guild)

        if ban is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"Ten ban nie istnieje!"
            ))
            return

        await ban.remove()

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Odbanowano {ban.user.name}#{ban.user.discriminator}"
        ))


def setup(client: main.MemiarzeClient):
    client.add_cog(Bans(client))
