from matplotlib import pyplot as plot
import discord
from discord.ext import commands
import main
from utils import math
import random


class Market(commands.Cog):

    testMarketBalance = 0
    testCashBalance = 100000000000
    currMultiplier = 1
    depositedMultiplier = currMultiplier
    decider = .5

    name = "Market"

    def __init__(self, client):
        self.client: main.MemiarzeClient = client
    
    @commands.command(name="deposit_to_market", aliases=["depm", "deposit_market", "deposit_to_m"])
    async def deposit_to_market(self, ctx: commands.Context, amount):
        if amount.lower() == "all":
            amount = self.testCashBalance
        else:
            amount = int(amount)
        
        self.testMarketBalance += amount
        self.testCashBalance -= amount

        self.depositedMultiplier = self.currMultiplier

        await ctx.send(f"{self.testMarketBalance} {self.testCashBalance}")

    @commands.command(name="withdraw_from_market", aliases=["withm", "withdraw_market", "withdraw_from_m"])
    async def withdraw_from_market(self, ctx: commands.Context, amount):
        if amount.lower() == "all":
            amount = self.testMarketBalance
        else:
            amount = int(amount)

        gotMoney: int = round(amount * (self.currMultiplier / self.depositedMultiplier))

        self.testCashBalance += gotMoney
        self.testMarketBalance -= amount

        await ctx.send(f"{gotMoney} {self.testMarketBalance} {self.testCashBalance}")
    
    @commands.command(name="new_multiplier", aliases=["nmp"])
    async def new_multiplier(self, ctx: commands.Context):
        if random.randint(0, 1):
            self.decider += random.uniform(.05, .15)
        else:
            self.decider -= random.uniform(.05, .15)
        
        if self.decider > 1 or self.decider < 0:
            self.decider = .49

        self.currMultiplier = math.calcNextNumber(self.currMultiplier, self.decider >= .5)

        await ctx.send(f"{self.currMultiplier} {self.decider}")

def setup(client: main.MemiarzeClient):
    client.add_cog(Market(client))
