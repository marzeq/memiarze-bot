import discord
from discord.ext import commands
import main
import utils
import orm.reaction_role


class ReactionRoles(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.group(name="reaction_role", aliases=["reactionrole", "rrole"], invoke_without_command=True)
    async def reaction_role(self, ctx: commands.Context):
        await ctx.send(
            embed=utils.ErrorEmbed(
                title="reaction_role",
                description="Nie znaleziono tej podkomendy"
            )
        )

    @reaction_role.command(name="add")
    async def add(self, ctx: commands.Context, message: discord.Message, mode: str = "default"):
        emojis = {}

        if mode not in ["default", "normal", "invert", "opposite"]:
            await ctx.send(
                embed=utils.ErrorEmbed(
                    title="reaction_role",
                    description="Zła wartość argumentu mode"
                )
            )

        await ctx.send(
            embed=utils.SuccessEmbed(
                title=f"OK, zostanie utworzone reaction role na wiadomości {message.jump_url}.",
                description="Teraz wpisz, jakie emoji ma być przypisane, do jakiej roli w tym formacie: `emoji id_roli` lub `emoji mention_roli`.\n"
                            "Na przykład `🏓 872965471524508534`.\n\n"
                            "Kiedy skończysz dodawać emoji, wpisz `ok` lub `finish`.\n"
                            "Jeśli się rozmyślisz, wpisz `stop` lub `cancel`."
            )
        )

        while True:
            emojimsg: discord.Message = await self.client.wait_for("message", check=lambda msg: msg.author.id == ctx.author.id)
            if emojimsg.content in ["ok", "finish"]:
                break
            elif emojimsg.content in ["stop", "cancel"]:
                await ctx.send(
                    embed=utils.ErrorEmbed(
                        title=f"Anulowano tworzenie reaction role na wiadomości {message.jump_url}."
                    )
                )

                return
            try:
                emojimsg.content.split(" ")[1]
            except:
                await ctx.send(
                    embed=utils.ErrorEmbed(
                        title="reaction_role",
                        description="Zły format"
                    )
                )

                return

            try:
                role: discord.Role = await commands.RoleConverter().convert(ctx, emojimsg.content.split(" ")[1])
            except commands.errors.RoleNotFound:
                await ctx.send(
                    embed=utils.ErrorEmbed(
                        title="reaction_role",
                        description=f"Nie znaleziono roli {emojimsg.content.split(' ')[1]}"
                    )
                )

                continue
            emoji: str = emojimsg.content.split(" ")[0]

            emojis[emoji] = role

            await ctx.send(
                embed=utils.SuccessEmbed(
                    title=f"Przypisano emoji {emoji} do roli {role.name}.",
                    description="Kiedy skończysz dodawać emoji, wpisz `ok` lub `finish`.\n"
                                "Jeśli się rozmyślisz, wpisz `stop` lub `cancel`."
                )
            )

        reaction_role_orm = orm.reaction_role.ReactionRoleMessages(self.client)

        await reaction_role_orm.create(message, mode, emojis)

        await ctx.send(
            embed=utils.SuccessEmbed(
                title=f"Pomyślnie dodano reaction role na wiadomości {message.jump_url}."
            )
        )


def setup(client: main.MemiarzeClient):
    client.add_cog(ReactionRoles(client))
