import discord
import main
import math


class Warn:
    def __init__(self, user: discord.User, reason: str, warnid: int, client: main.MemiarzeClient, guild: discord.Guild):
        self.user = user
        self.reason = reason
        self.id = warnid
        self.__client = client
        self.guild = guild

    def __repr__(self):
        return f"ID ostrzeżenia: #{self.id} | Użytkownik: {self.user.name}#{self.user.discriminator} | " \
               f"Powód: {self.reason}"

    def __str__(self):
        return self.__repr__()

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

    def create(self, user: discord.User, guild: discord.Guild, reason: str):
        self.client.cursor.execute("insert into warns (userid, reason, guildid) values (:userid, :reason, :guildid)",
                                   {"userid": user.id,
                                    "reason": reason,
                                    "guildid": guild.id})
        self.client.conn.commit()

        self.client.cursor.execute("select * from warns where userid = :userid and guildid = :guildid",
                                   {"userid": user.id,
                                    "guildid": guild.id})

        fetched = self.client.cursor.fetchall()
        fetched.reverse()
        warnid = fetched[0][2]

        return Warn(user, reason, warnid, self.client, guild)

    def get_user_warns(self, user: discord.User, guild: discord.Guild):
        self.client.cursor.execute("select * from warns where userid = :userid and guildid = :guildid",
                                   {"userid": user.id,
                                    "guildid": guild.id})

        fetched = self.client.cursor.fetchall()

        warns = []

        for obj in fetched:
            warns.append(Warn(self.client.get_user(obj[0]), obj[1], obj[2], self.client, guild))

        return warns

    def get_warn_by_id(self, warnid: int):
        self.client.cursor.execute("select * from warns where id = :id", {"id": warnid})

        fetched = self.client.cursor.fetchone()

        if not fetched:
            return None

        return Warn(self.client.get_user(fetched[0]), fetched[1], fetched[2],
                    self.client, self.client.get_guild(fetched[3]))