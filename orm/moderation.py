import discord
import main
import math


class Warn:
    def __init__(self, user: discord.User, reason: str, warnid: int, client: main.MemiarzeClient):
        self.user = user
        self.reason = reason
        self.id = warnid
        self.__client = client

    def __repr__(self):
        return f"Warn ID: #{self.id} | User: {self.user.name}#{self.user.discriminator} | Reason: {self.reason}"

    def __str__(self):
        return f"Warn ID: #{self.id} | User: {self.user.name}#{self.user.discriminator} | Reason: {self.reason}"

    def remove(self):
        self.__client.cursor.execute("delete from warns where id = :id", {"id": self.id})

    def change_reason(self, reason: str):
        self.__client.cursor.execute("update warns set reason = :reason where id = :id", {"reason": reason,
                                                                                          "id": self.id})
        self.reason = reason

        return self

    def change_user(self, user: discord.User):
        self.__client.cursor.execute("update warns set userid = :userid where id = :id", {"userid": user.id,
                                                                                          "id": self.id})
        self.user = user

        return self


class Warns:
    def __init__(self, client: main.MemiarzeClient):
        self.client = client

    def create(self, user: discord.User, reason: str):
        self.client.cursor.execute("insert into warns (userid, reason) values (:userid, :reason)", {"userid": user.id,
                                                                                                    "reason": reason})
        self.client.conn.commit()

        self.client.cursor.execute("select * from warns where userid = :userid", {"userid": user.id})

        fetched = self.client.cursor.fetchall()
        fetched.reverse()
        warnid = fetched[0][2]

        return Warn(user, reason, warnid, self.client)

    def get_user_warns(self, user: discord.User):
        self.client.cursor.execute("select * from warns where userid = :userid", {"userid": user.id})

        fetched = self.client.cursor.fetchall()

        warns = []

        for obj in fetched:
            warns.append(Warn(self.client.get_user(obj[0]), obj[1], obj[2], self.client))

        return warns

    def get_warn_by_id(self, warnid: int):
        self.client.cursor.execute("select * from warns where id = :id", {"id": warnid})

        fetched = self.client.cursor.fetchone()

        if not fetched:
            return None

        return Warn(self.client.get_user(fetched[0]), fetched[1], fetched[2], self.client)


class BaseMutes:
    def __init__(self, client: main.MemiarzeClient):
        self.client = client

    def get_mute_by_member(self, member: discord.Member):
        self.client.cursor.execute("select * from warns where memberid = :memberid", {"memberid": member.id})

        fetched = self.client.cursor.fetchone()

        if fetched is None:
            return None

        if fetched[2] is None:
            return Mute(self.client.get_guild(fetched[3]).get_member(fetched[0]), fetched[1], self.client)
        return TempMute(self.client.get_guild(fetched[3]).get_member(fetched[0]), fetched[1], fetched[2], self.client)


class Mutes(BaseMutes):
    async def create(self, member: discord.Member, reason: str):
        self.client.cursor.execute(
            "insert into mutes (memberid, reason, guildid) values (:memberid, :reason, :guildid)",
            {"memberid": member.id,
             "reason": reason,
             "guildid": member.guild.id}
        )

        self.client.conn.commit()

        assert isinstance(member.guild, discord.Guild)

        self.client.cursor.execute("select muteroleid from guilds where id = :id", {"id": member.guild.id})

        fetched = self.client.cursor.fetchone()

        if fetched == (None,):
            perms = discord.Permissions(send_messages=False, speak=False)
            role = await member.guild.create_role(name="Muted", permissions=perms)

            self.client.cursor.execute("update guilds set muteroleid = :roleid where id = :guildid", {
                "roleid": role.id,
                "guildid": member.guild.id
            })

            self.client.conn.commit()

            fetched = list(fetched)

            fetched[0] = role.id

        fetched = list(fetched)

        await member.add_roles(member.guild.get_role(fetched[0]), reason=reason)

        return Mute(member, reason, self.client)


class TempMutes(BaseMutes):
    async def create(self, member: discord.Member, reason: str, time: int):
        self.client.cursor.execute(
            "insert into mutes (memberid, reason, time, guildid) values (:memberid, :reason, :time, :guildid)",
            {"memberid": member.id,
             "reason": reason,
             "time": time,
             "guildid": member.guild.id}
        )

        self.client.conn.commit()

        assert isinstance(member.guild, discord.Guild)

        self.client.cursor.execute("select muteroleid from guilds where id = :id", {"id": member.guild.id})

        fetched = self.client.cursor.fetchone()

        if fetched == (None,):
            perms = discord.Permissions(send_messages=False, speak=False)
            role = await member.guild.create_role(name="Muted", permissions=perms)

            self.client.cursor.execute("update guilds set muteroleid = :roleid where id = :guildid", {
                "roleid": role.id,
                "guildid": member.guild.id
            })

            self.client.conn.commit()

            fetched = list(fetched)

            fetched[0] = role.id

        fetched = list(fetched)

        await member.add_roles(member.guild.get_role(fetched[0]), reason=reason)

        return TempMute(member, reason, time, self.client)

    def get_mutes_before(self, time: float):
        fetched = self.client.cursor.execute("select * from mutes where time <= :timenow", {
            "timenow": math.floor(time)}).fetchall()

        tempmutes = []

        for obj in fetched:
            tempmutes.append(TempMute(self.client.get_guild(obj[3]).get_member(obj[0]),
                                      obj[1], obj[2], self.client))

        return tempmutes


class BaseMute:
    def __init__(self, member: discord.Member, reason: str, client: main.MemiarzeClient):
        self.member = member
        self.__client = client
        self.user: discord.User = self.__client.get_user(member.id)
        self.reason = reason

    def __repr__(self):
        return f"Member: {self.user.name}#{self.user.discriminator} | Reason: {self.reason}"

    def __str__(self):
        return f"Member: {self.user.name}#{self.user.discriminator} | Reason: {self.reason}"

    async def remove(self):
        self.__client.cursor.execute("delete from mutes where memberid = :memberid", {"memberid": self.member.id})
        self.__client.cursor.execute("select muteroleid from guilds where id = :id", {"id": self.member.guild.id})

        fetched = self.__client.cursor.fetchone()

        if fetched == (None,):
            raise ValueError("Mute role not set up!")

        await self.member.remove_roles(self.member.guild.get_role(fetched[0]), reason="Unmute")

    def change_reason(self, reason: str):
        self.__client.cursor.execute("update mutes set reason = :reason where memberid = :memberid", {
            "reason": reason,
            "memberid": self.member.id
        })
        self.reason = reason

        return self


class Mute(BaseMute):
    pass


class TempMute(BaseMute):
    def __init__(self, member: discord.Member, reason: str, time: int, client: main.MemiarzeClient):
        self.time = time
        super().__init__(member, reason, client)

    def change_time(self, time: int):
        self.__client.cursor.execute("update mutes set time = :time where memberid = :memberid", {
            "time": time,
            "memberid": self.member.id
        })
        self.time = time

        return self
