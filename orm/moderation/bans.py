import discord
import main
import math


class BaseBans:
    def __init__(self, client: main.MemiarzeClient):
        self.client = client

    async def get_ban_by_member(self, member: discord.User, guild: discord.Guild):
        self.client.cursor.execute("select * from bans where memberid = :memberid and guildid = :guildid", {"memberid": member.id, "guildid": guild.id})

        fetched = self.client.cursor.fetchone()

        if fetched is None:
            return None

        if fetched[2] is None:
            return Ban(await self.client.fetch_user(fetched[0]), await self.client.fetch_guild(fetched[3]), fetched[1], self.client)
        return TempBan(await self.client.fetch_user(fetched[0]), await self.client.fetch_guild(fetched[3]),
                       fetched[1], fetched[2], self.client)


class Bans(BaseBans):
    async def create(self, member: discord.Member, reason: str):
        self.client.cursor.execute(
            "insert into bans (memberid, reason, guildid) values (:memberid, :reason, :guildid)",
            {"memberid": member.id,
             "reason": reason,
             "guildid": member.guild.id}
        )

        self.client.conn.commit()

        assert isinstance(member.guild, discord.Guild)

        await member.ban(reason=reason)

        return Ban(await self.client.fetch_user(member.id), member.guild, reason, self.client)


class TempBans(BaseBans):
    async def create(self, member: discord.Member, reason: str, time: int):
        self.client.cursor.execute(
            "insert into bans (memberid, reason, time, guildid) values (:memberid, :reason, :time, :guildid)",
            {"memberid": member.id,
             "reason": reason,
             "time": time,
             "guildid": member.guild.id}
        )

        self.client.conn.commit()

        assert isinstance(member.guild, discord.Guild)

        await member.ban(reason=reason)

        return TempBan(await self.client.fetch_user(member.id), member.guild, reason, time, self.client)

    async def get_bans_before(self, time: float):
        fetched = self.client.cursor.execute("select * from bans where time <= :timenow", {
            "timenow": math.floor(time)}).fetchall()

        tempbans = []

        for obj in fetched:
            tempbans.append(TempBan(await self.client.fetch_user(obj[0]), self.client.get_guild(obj[3]),
                                    obj[1], obj[2], self.client))

        return tempbans


class BaseBan:
    def __init__(self, user: discord.User, guild: discord.Guild, reason: str, client: main.MemiarzeClient):
        self.user = user
        self.__client = client
        self.reason = reason
        self.guild = guild

    def __repr__(self):
        return f"Członek: {self.user.name}#{self.user.discriminator} | Powód: {self.reason}"

    def __str__(self):
        return self.__repr__()

    async def remove(self):
        self.__client.cursor.execute("delete from bans where memberid = :memberid", {"memberid": self.user.id})
        self.__client.conn.commit()

        await self.guild.unban(self.user, reason="Unban")

    def change_reason(self, reason: str):
        self.__client.cursor.execute("update bans set reason = :reason where memberid = :memberid", {
            "reason": reason,
            "memberid": self.user.id
        })
        self.reason = reason

        return self


class Ban(BaseBan):
    pass


class TempBan(BaseBan):
    def __init__(self, user: discord.User, guild: discord.Guild, reason: str, time: int, client: main.MemiarzeClient):
        self.time = time
        super().__init__(user, guild, reason, client)

    def change_time(self, time: int):
        self.__client.cursor.execute("update bans set time = :time where memberid = :memberid", {
            "time": time,
            "memberid": self.user.id
        })
        self.time = time

        return self
