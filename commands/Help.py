import discord
from discord.ext import commands
import main
import utils


class Help(commands.Cog):

    name = "Help"

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.command(name="help", aliases=["commands"])
    async def help(self, ctx: commands.Context, page: int = 1):
        page -= 1
        categorised = {}
        for cog in self.client.cogs:
            categorised[cog] = []
        for command in self.client.commands:
            categorised[command.cog.name].append(utils.get_command_usage(command))

        categorised_eachn = []
        temp = []
        for cog in categorised.items():
            if len(temp) == 5:
                categorised_eachn.append(temp)
                temp = []
            temp.append(cog)

        embed = utils.SuccessEmbed(
            title="Oto dostępne komendy:",
            description="(Reszta komend może być na innych stronach.\n"
                        "Aby je zobaczyć wpisz `help <strona>`.)"
        )
        embed.set_footer(text=f"Strona {page+1}/{len(categorised_eachn)}")

        if page >= len(categorised_eachn) or page < 0:
            await ctx.send(embed=utils.ErrorEmbed(
                title="help",
                description="Ta strona nie istnieje!"
            ))

            return

        for cog, usages in categorised_eachn[page]:
            joined = "\n\n".join(usages)
            if joined:
                embed.add_field(name=cog, value=f"```\n{joined}\n```", inline=False)

        await ctx.send(embed=embed)


def setup(client: main.MemiarzeClient):
    client.add_cog(Help(client))
