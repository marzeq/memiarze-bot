import discord
from discord.ext import commands
import main
import utils
import orm.moderation
import time
import os


class Warns(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.command(name="warn")
    async def warn(self, ctx: commands.Context, user: discord.User, *, reason: str = "No reason provided!"):
        warns_orm = orm.moderation.Warns(self.client)
        warning: orm.moderation.Warn = warns_orm.create(user, reason)

        await ctx.send(embed=utils.SuccessEmbed(title=f"Warned {user.name}#{user.discriminator} for: \"{reason}\"")
                       .set_footer(text=f"Warn ID: {warning.id}"))

    @commands.command(name="warnings", aliases=["warns"])
    async def warnings(self, ctx: commands.Context, user: discord.User):
        warns_orm = orm.moderation.Warns(self.client)

        warns = [str(warnin) for warnin in warns_orm.get_user_warns(user)]

        desc = "```\n" + "\n".join(warns) + "\n```"

        if not warns:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"{user.name}#{user.discriminator} doesn't have any warnings!"
            ))
        elif len(desc) <= 2048:
            await ctx.send(embed=utils.SuccessEmbed(
                title=f"Warnings for {user.name}#{user.discriminator}:",
                description=desc
            ))
        else:
            timern = str(time.time())
            with open(f"temp/warns{timern}.txt", "w") as f:
                f.write(desc)
            await ctx.send(embed=utils.ErrorEmbed(
                title="This embed was too big so we sent all the files along with this message",
            ), file=discord.File(f"./temp/warns{timern}.txt", filename="warns.txt"))
            os.remove(f"./temp/warns{timern}.txt")

    @commands.command(name="warn_reason", aliases=["warnreason"])
    async def warn_reason(self, ctx: commands.Context, warnid: int, *, reason: str):
        warns_orm = orm.moderation.Warns(self.client)

        selectedwarn: orm.moderation.Warn = warns_orm.get_warn_by_id(warnid)

        if selectedwarn is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"The warn with the ID of {warnid} doesn't exist!"
            ))
            return

        selectedwarn.change_reason(reason)

    @commands.command(name="warn_user", aliases=["warnuser"])
    async def warn_user(self, ctx: commands.Context, warnid: int, user: discord.User):
        warns_orm = orm.moderation.Warns(self.client)

        selectedwarn: orm.moderation.Warn = warns_orm.get_warn_by_id(warnid)

        if selectedwarn is None:
            await ctx.send(embed=utils.ErrorEmbed(
                title=f"The warn with the ID of {warnid} doesn't exist!"
            ))
            return

        selectedwarn.change_user(user)


def setup(client: main.MemiarzeClient):
    client.add_cog(Warns(client))
