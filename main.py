import json
import os
from typing import *

import discord
from discord.ext import commands

import utils

import sqlite3


__version__ = "1.1"


class MemiarzeClient(commands.Bot):

    default_prefix = "./"

    async def get_prefix(self, message: discord.Message):
        if message.guild is None:
            return self.default_prefix

        self.cursor.execute("select commandprefix from guilds where id = :id", {"id": message.guild.id})

        fetched = self.cursor.fetchone()

        if fetched is None:
            return self.default_prefix

        return fetched[0]

    def __init__(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor, **options):
        r"""
        :param conn: sqlite3.Connection
        :param cursor: sqlite3.Cursor
        :param options: kwargs
        """
        self.conn = conn
        self.cursor = cursor
        super().__init__(command_prefix=self.get_prefix, **options)

    async def load_extensions(self, dirs: List[str]):
        r"""
        Load all extensions (cogs).

        :param dirs: List[str]
        :return: None
        """
        for directory in dirs:
            for filename in os.listdir(f"{directory}"):
                if filename.endswith(".py"):
                    self.load_extension(f"{directory}.{filename[:-3]}")
                    print(f"Registered {directory}.{filename[:-3]}")

    async def on_command_error(self, ctx: commands.Context, exception):
        r"""
        Listener that runs everytime a command encounters an exception.

        :param ctx: discord.ext.commands.Context
        :param exception: Any class that extends Exception
        :return: None
        """
        try:
            exception.original
        except AttributeError:
            exception.original = exception
        finally:
            exception = exception.original
            tpe = type(exception)

        if tpe == discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.send(embed=utils.ErrorEmbed(
                title=ctx.command.name,
                description=f"Nie podano argumentu {exception.param.name}!")
            )
        elif tpe == discord.ext.commands.errors.CommandNotFound:
            await ctx.send(
                embed=utils.ErrorEmbed(
                    title="main",
                    description="Komenda nie znaleziona"
                )
            )
        else:
            await ctx.send(
                embed=utils.ErrorEmbed(
                    title=ctx.command.name,
                    description="`" + str(type(exception)).replace("<class '", "").
                                replace("'>", "") + "`: " + str(exception)
                )
            )
            raise exception

    async def on_ready(self):
        r"""
        Listener that listens for when the bot is ready.

        :return: None
        """
        print(f"Logged in as {self.user.name}#{self.user.discriminator}!")

        self.remove_command("help")
        print("Registering extensions...")
        await self.load_extensions(["commands", "listeners", "loops"])
        print("Registered all extensions")


if __name__ == '__main__':
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        TOKEN = config["token"]

    connec = sqlite3.connect(config["db"]["filename"])

    client = MemiarzeClient(conn=connec, cursor=connec.cursor(), intents=discord.Intents.all())

    print("Logging in...")
    client.run(TOKEN)
