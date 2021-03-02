import discord
from discord.ext import commands
import main
import orm.reaction_role


class ReactionRoleEvent(commands.Cog):

    def __init__(self, client):
        self.client: main.MemiarzeClient = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel: discord.TextChannel = await self.client.fetch_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)

        reaction_role_orm = orm.reaction_role.ReactionRoleMessages(self.client)

        reaction_role_message = await reaction_role_orm.get_reaction_role_by_message(message)

        if reaction_role_message is None:
            return

        member: discord.Member = payload.member

        user: discord.User = await self.client.fetch_user(payload.member.id)

        if user.bot: return

        if str(payload.emoji) not in reaction_role_message.emojis.keys(): return

        if reaction_role_message.mode in ["normal", "default"]:
            await member.add_roles(reaction_role_message.emojis[str(payload.emoji)].role)
        elif reaction_role_message.mode in ["invert", "opposite"]:
            await member.remove_roles(reaction_role_message.emojis[str(payload.emoji)].role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        channel: discord.TextChannel = await self.client.fetch_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)

        reaction_role_orm = orm.reaction_role.ReactionRoleMessages(self.client)

        reaction_role_message = await reaction_role_orm.get_reaction_role_by_message(message)

        if reaction_role_message is None:
            return

        member: discord.Member = await channel.guild.fetch_member(payload.user_id)

        user: discord.User = await self.client.fetch_user(payload.user_id)

        if user.bot: return

        if str(payload.emoji) not in reaction_role_message.emojis.keys(): return

        if reaction_role_message.mode in ["normal", "default"]:
            await member.remove_roles(reaction_role_message.emojis[str(payload.emoji)].role)
        elif reaction_role_message.mode in ["invert", "opposite"]:
            await member.add_roles(reaction_role_message.emojis[str(payload.emoji)].role)


def setup(client: main.MemiarzeClient):
    client.add_cog(ReactionRoleEvent(client))
