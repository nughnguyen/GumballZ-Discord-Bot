import discord
from core import gumballz, Cog
from discord.ext import commands
from discord.ui import Button, View


class GuildJoinDM(Cog):
    """Sends a thank-you DM to whoever added the bot to a guild."""

    def __init__(self, bot: gumballz):
        self.bot = bot

    @commands.Cog.listener(name="on_guild_join")
    async def send_msg_to_adder(self, guild: discord.Guild):
        async for entry in guild.audit_logs(limit=3):
            if entry.action != discord.AuditLogAction.bot_add:
                continue

            embed = discord.Embed(
                description=(
                    "<:module:1453391552029135000> **Thanks for adding me.**\n\n"
                    "<a:ArrowRed:1453413846755578079> My default prefix is `>`\n"
                    "<a:ArrowRed:1453413846755578079> Use the `>help` command to see a list of commands\n"
                    "<a:ArrowRed:1453413846755578079> For detailed guides, FAQ and information, visit our **[Support Server](https://dsc.gg/thenoicez)**"
                ),
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url=entry.user.avatar.url if entry.user.avatar else entry.user.default_avatar.url
            )
            if guild.icon:
                embed.set_author(name=guild.name, icon_url=guild.icon.url)
            else:
                embed.set_author(name=guild.name, icon_url=guild.me.display_avatar.url)

            view = View()
            view.add_item(Button(label="Support", style=discord.ButtonStyle.link, url="https://dsc.gg/thenoicez"))

            try:
                await entry.user.send(embed=embed, view=view)
            except Exception as e:
                print(e)
            return
