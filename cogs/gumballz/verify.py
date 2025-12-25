import discord 
from discord .ext import commands 

class _verify(commands .Cog ):
    def __init__ (self ,bot ):
        self.bot=bot 

    """Verification commands help"""

    def help_custom (self ):
        emoji ='<:thunder:1453394963780862117>'
        label ="Verification Commands"
        description ="Show you the commands of Verification"
        return emoji ,label ,description 

    @commands .group ()
    async def __Verification__ (self ,ctx :commands .Context ):
        """`verification setup`, `verification status`, `verification enable`, `verification disable`, `verification logs`, `verification reset`, `verification verify`, `verification fix`"""
        pass 

async def setup (bot ):
    await bot.add_cog(_verify(bot))
