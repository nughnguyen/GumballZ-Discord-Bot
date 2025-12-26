import discord
from discord.ext import commands

class _games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""
  
    def help_custom(self):
		      emoji = '<:games:1453391627329470726>'
		      label = "Games Commands"
		      description = "Show you Commands of Games"
		      return emoji, label, description

    @commands.group(name="Games")
    async def _Games(self, ctx: commands.Context):
        """blackjack , baucua, chess , tic-tac-toe , country-guesser , rps , lights-out , wordle , 2048 , memory-game , number-slider , battleship , connect-four , slots, counting"""