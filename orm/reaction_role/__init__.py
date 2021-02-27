import discord
import main
from typing import *


class ReactionRoleMessages:
    def __init__(self, client: main.MemiarzeClient):
        self.client = client

    async def get_reaction_role_by_message(self, message: discord.Message):
        self.client.cursor.execute("select * from reaction_role where messageid = :messageid",
                                   {"messageid": message.id})

        fetched_first = self.client.cursor.fetchone()

        if fetched_first is None:
            return None

        self.client.cursor.execute("select * from reaction_role_emoji where messageid = :messageid",
                                   {"messageid": message.id})

        fetched = self.client.cursor.fetchall()
        emojis = {}
        for emoji in fetched:
            emojis[emoji[0]] = ReactionRoleEmoji(emoji[0], message.channel.guild.get_role(emoji[2]))

        return ReactionRoleMessage(message, fetched_first[1], emojis, self.client)

    async def create(self, message: discord.Message, mode: str, emojis: Dict[str, discord.Role]):
        emojis_to_class = {}
        for emoji, role in emojis.items():
            self.client.cursor.execute("insert into reaction_role_emoji (emoji, messageid, roleid) values (:emoji, :messageid, :roleid)",
                                       {"emoji": emoji, "messageid": message.id, "roleid": role.id})

            emojis_to_class[emoji] = ReactionRoleEmoji(emoji, role)

            await message.add_reaction(emoji)

        self.client.cursor.execute("insert into reaction_role (messageid, mode) values (:messageid, :mode)",
                                   {"messageid": message.id, "mode": mode})

        self.client.conn.commit()

        return ReactionRoleMessage(message, mode, emojis_to_class, self.client)


class ReactionRoleEmoji:
    def __init__(self, emoji: str, role: discord.Role):
        self.emoji = emoji
        self.role = role


class ReactionRoleMessage:
    def __init__(self, message: discord.Message, mode: str, emojis: Dict[str, ReactionRoleEmoji], client: main.MemiarzeClient):
        self.message = message
        self.mode = mode
        self.emojis = emojis
        self.client = client

    async def remove(self):
        self.client.cursor.execute("delete from reaction_role where messageid = :messageid", {"messageid": self.message.id})
        self.client.cursor.execute("delete from reaction_role_emoji where messageid = :messageid", {"messageid": self.message.id})

        self.client.conn.commit()

        await self.message.clear_reactions()
