from utils import getConfig
import discord
from discord.ext import commands
from utils.Tools import get_ignore_data
import aiosqlite

class MentionDropdown(discord.ui.Select):
    def __init__(self, message: discord.Message, bot: commands.Bot, prefix: str):
        self.message = message
        self.bot = bot
        self.prefix = prefix
        options = [
            discord.SelectOption(label="Home", emoji="<:index:1453391645382017064>", description="Go to the main menu"),
            discord.SelectOption(label="Developer Info", emoji="<:codebase:1453391605565231105>", description="See who created me"),
            discord.SelectOption(label="Links", emoji="<:links:1453394953941024798>", description="Useful bot links"),
        ]
        super().__init__(placeholder="Start With GumballZ", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.message.author.id:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)

        embed = discord.Embed(color=0xFF0000)  # Red
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        if self.values[0] == "Home":
            embed.title = f"{self.message.guild.name}"
            embed.description = (
                f"> <:heart3:1453391634573299833> **Hey {interaction.user.mention}**\n"
                f"> <a:ArrowRed:1453413846755578079> **Prefix For This Server: `{self.prefix}`**\n\n"
                f"___Type `{self.prefix}help` for more information.___"
            )
        elif self.values[0] == "Developer Info":
            embed.title = "<:codebase:1453391605565231105> Developer"
            embed.description = (
                "There are only 1 Founder Who Created Me. Thanks You To Him 💞.\n\n"
                "**The Founder**\n"
                "**[01]. [Nguyen Quoc Hung](https://discord.com/users/561443914062757908)**"
            )
        elif self.values[0] == "Links":
            embed.title = "<:links:1453394953941024798> Important Links"
            embed.description = (
                "**[Invite GumballZ](https://discord.com/oauth2/authorize?client_id=1305035261897343026)**\n"
                "**[Join Support Server](https://dsc.gg/thenoicez)**"
            )

        embed.set_footer(text="Powered by GumballZ™", icon_url=self.bot.user.avatar.url)
        await interaction.response.edit_message(embed=embed, view=self.view)

class MentionView(discord.ui.View):
    def __init__(self, message: discord.Message, bot: commands.Bot, prefix: str):
        super().__init__(timeout=None)
        self.add_item(MentionDropdown(message, bot, prefix))


class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xFF0000  # Full red
        self.bot_name = "GumballZ"

    async def is_blacklisted(self, message):
        async with aiosqlite.connect("db/block.db") as db:
            cursor = await db.execute("SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (message.guild.id,))
            if await cursor.fetchone():
                return True
            cursor = await db.execute("SELECT 1 FROM user_blacklist WHERE user_id = ?", (message.author.id,))
            if await cursor.fetchone():
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if await self.is_blacklisted(message):
            return

        ignore_data = await get_ignore_data(message.guild.id)
        if str(message.author.id) in ignore_data["user"] or str(message.channel.id) in ignore_data["channel"]:
            return

        if self.bot.user in message.mentions and len(message.content.strip().split()) == 1:
            guild_id = message.guild.id
            data = await getConfig(guild_id)
            prefix = data["prefix"]

            embed = discord.Embed(
                title=f"{message.guild.name}",
                description=f"> <:heart3:1453391634573299833> **Hey {message.author.mention}**\n"
                            f"> <a:ArrowRed:1453413846755578079> **Prefix For This Server: `{prefix}`**\n\n"
                            f"___Type `{prefix}help` for more information.___",
                color=self.color
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text="Powered by GumballZ™", icon_url=self.bot.user.avatar.url)

            view = MentionView(message, self.bot, prefix)
            await message.channel.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Mention(bot))
