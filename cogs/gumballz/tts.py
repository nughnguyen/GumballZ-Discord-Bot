import discord
from discord.ext import commands


class _tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """TTS commands"""

    def help_custom(self):
        emoji = '🔊'
        label = "TTS Commands"
        description = "Text-to-Speech voice commands"
        return emoji, label, description

    @commands.group()
    async def __TTS__(self, ctx: commands.Context):
        """`say` , `tts set` , `tts clear` , `tts status`"""
