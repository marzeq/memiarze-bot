import discord


class SuccessEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs['colour'] = 0x42f557
        super().__init__(**kwargs)


class ErrorEmbed(discord.Embed):
    def __init__(self, **kwargs):
        kwargs['colour'] = 0xf54242
        super().__init__(**kwargs)
