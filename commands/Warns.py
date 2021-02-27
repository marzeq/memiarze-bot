import discord
from discord.ext import commands
import main
import utils
import orm.moderation
import time
import os


class Warns(commands.Cog):

    name = "Warns"

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.command(name="warn")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def warn(self, ctx: commands.Context, user: discord.User, *, reason: str = "Nie podano powodu!"):
        warns_orm = orm.moderation.Warns(self.client)
        warning: orm.moderation.Warn = warns_orm.create(user, ctx.guild, reason)

        await ctx.send(embed=utils.SuccessEmbed(title=f"Ostrzeżono {user.name}#{user.discriminator} za: \"{reason}\"")
                       .set_footer(text=f"ID ostrzeżenia: {warning.id}"))

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def warnings(self, ctx: commands.Context, user: discord.User):
        warns_orm = orm.moderation.Warns(self.client)

        warns = [str(warnin) for warnin in warns_orm.get_user_warns(user, ctx.guild)]

        desc = "```\n" + "\n".join(warns) + "\n```"

        if not warns:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"{user.name}#{user.discriminator} nie ma żadnych ostrzeżeń!"
            ))
        elif len(desc) <= 2048:
            await ctx.send(embed=utils.SuccessEmbed(
                title=f"Ostrzeżenia dla {user.name}#{user.discriminator}:",
                description=desc
            ))
        else:
            timern = str(time.time())
            with open(f"temp/warns{timern}.txt", "w") as f:
                f.write(desc)
            await ctx.send(embed=utils.ErrorEmbed(
                title="Ten embed był za duży, więc wysłaliśmy wszystkie ostrzeżenia w pliku wyżej",
            ), file=discord.File(f"./temp/warns{timern}.txt", filename="warns.txt"))
            os.remove(f"./temp/warns{timern}.txt")

    @commands.command(name="warn_reason", aliases=["warnreason"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def warn_reason(self, ctx: commands.Context, warnid: int, *, reason: str):
        warns_orm = orm.moderation.Warns(self.client)

        selectedwarn: orm.moderation.Warn = warns_orm.get_warn_by_id(warnid)

        if selectedwarn is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"Ostrzeżenie o ID {warnid} nie istnieje!"
            ))
            return

        selectedwarn.change_reason(reason)

    @commands.command(name="warn_user", aliases=["warnuser"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def warn_user(self, ctx: commands.Context, warnid: int, user: discord.User):
        warns_orm = orm.moderation.Warns(self.client)

        selectedwarn: orm.moderation.Warn = warns_orm.get_warn_by_id(warnid)

        if selectedwarn is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"Ostrzeżenie o ID {warnid} nie istnieje!"
            ))
            return

        selectedwarn.change_user(user)

    @commands.command(name="removewarn", aliases=["remove_warn"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def removewarn(self, ctx: commands.Context, warnid: int):
        warns_orm = orm.moderation.Warns(self.client)

        selectedwarn: orm.moderation.Warn = warns_orm.get_warn_by_id(warnid)

        if selectedwarn is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"Ostrzeżenie o ID {warnid} nie istnieje!"
            ))
            return

        if selectedwarn.guild.id != ctx.guild.id:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"Ostrzeżenie o ID {warnid} pochodzi z innej gildii!"
            ))
            return

        selectedwarn.remove()

        await ctx.send(embed=utils.SuccessEmbed(
            title=f"Usunięto ostrzeżenie #{selectedwarn.id}"
                  f" ({selectedwarn.user.name}#{selectedwarn.user.discriminator})",
        ))


def setup(client: main.MemiarzeClient):
    client.add_cog(Warns(client))
