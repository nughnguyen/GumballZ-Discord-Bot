import discord
from discord.ext import commands
import asyncio

class React(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        for owner in self.bot.owner_ids:
            if f"<@{owner}>" in message.content:
                try:
                    if owner == 561443914062757908:
                        emojis = [
                            "<a:BlackCrown:1453395740264235038>",
                            "<a:Active_Developer:1453395737290473513>",
                            "<a:staff:1453395720316125284>",
                            "<a:mingle:1453779759283572787>"                         ]
                    else:
                        emojis = [
                            "<a:BlackCrown:1453395740264235038>",
                            "<a:Active_Developer:1453395737290473513>",
                            "<a:staff:1453395720316125284>"
                        ]

                    for emoji in emojis:
                        try:
                            await message.add_reaction(emoji)
                        except discord.HTTPException:
                            pass  # ignore if emoji is invalid or not accessible

                except discord.errors.RateLimited as e:
                    await asyncio.sleep(e.retry_after)
                except Exception as e:
                    print(f"An unexpected error occurred Auto react owner mention: {e}")